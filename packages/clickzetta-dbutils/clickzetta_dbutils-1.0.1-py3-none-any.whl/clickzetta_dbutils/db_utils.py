import json
import os
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional, Dict

from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.engine import URL
from sqlalchemy.engine.base import Engine


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass


@dataclass
class ConnectionConfig:
    dsName: str
    dsType: int
    schema: str
    host: Optional[str] = None
    magicToken: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    instanceName: Optional[str] = None
    workspaceName: Optional[str] = None
    options: Dict[str, str] = field(default_factory=dict)


class DatabaseConnectionManager:
    """
    Manages database connections with flexible configuration options.
    """

    def __init__(self):
        """
        Initialize a database connection for a specific data source.
        """
        self._vcluster: Optional[str] = None
        self._workspace: Optional[str] = None
        self._driver: Optional[str] = None
        self._schema: Optional[str] = None
        self._engine: Optional[Engine] = None
        self._options = {}

    @classmethod
    def _load_connection_configs(cls) -> Dict[str, ConnectionConfig]:
        """
        Load and cache connection configurations from environment variables.

        Returns:
            Dict of connection configurations keyed by data source name
        """
        if not hasattr(DatabaseConnectionManager, '_connection_cache'):
            # Retrieve and decode connection info from environment variable
            conn_info_str = os.environ.get('connectionInfos', '[]')
            decoded_info = urllib.parse.unquote(conn_info_str)
            conn_list = json.loads(decoded_info)

            # Create connection configs
            cls._connection_cache = {
                info.get('dsName'): ConnectionConfig(**info)
                for info in conn_list
            }
        return cls._connection_cache

    def get_connection_info(self, ds_name: str) -> ConnectionConfig:
        """
        Find connection info by data source name
        """
        connections = self._load_connection_configs()

        # Validate data source exists
        if ds_name not in connections:
            raise DatabaseConnectionError(f"Data source '{ds_name}' not found")

        config = connections.get(ds_name)
        config.options.update(self._options)
        return config

    def use_workspace(self, workspace: str) -> 'DatabaseConnectionManager':
        """
        Set workspace for the connection.

        Args:
            workspace (str): Workspace name

        Returns:
            self: For method chaining
        """
        self._workspace = workspace
        return self

    def use_driver(self, driver: str) -> 'DatabaseConnectionManager':
        """
        Set driver for the connection.

        Args:
            driver (str): Driver name

        Returns:
            self: For method chaining
        """
        self._driver = driver
        return self

    def use_schema(self, schema: str) -> 'DatabaseConnectionManager':
        """
        Set schema for the connection.

        Args:
            schema (str): Schema name

        Returns:
            self: For method chaining
        """
        self._schema = schema
        return self

    def use_vcluster(self, vcluster: str) -> 'DatabaseConnectionManager':
        """
        Set virtual cluster for the connection.

        Args:
            vcluster (str): Virtual cluster name

        Returns:
            self: For method chaining
        """
        self._vcluster = vcluster
        return self

    def use_options(self, options):
        """
        Set additional connection options.

        Args:
            options (dict): Additional connection options

        Returns:
            self: For method chaining
        """
        if options:
            self._options.update(options)

    def connect(self, ds_name: str, *args, **kwargs) -> Engine:
        """
        Create SQLAlchemy engine based on data source name and optional schema

        :param ds_name: Name of the data source
        :return: SQLAlchemy Engine
        """
        conn_info: ConnectionConfig = self.get_connection_info(ds_name)

        if not conn_info.host:
            raise DatabaseConnectionError("Missing connection host for MySQL data source")

        ds_type = conn_info.dsType
        options = conn_info.options or {}
        schema = self._schema or conn_info.schema
        host_parts = conn_info.host.split(':')



        # Construct connection URL based on data source type
        if ds_type == 5:  # Mysql
            if not conn_info.username or not conn_info.password:
                raise DatabaseConnectionError("Missing username or password for MySQL data source")
            # Split host into host and port if provided

            url = URL.create(
                drivername=self._driver or 'mysql+mysqlconnector',
                username=conn_info.username,
                password=conn_info.password,
                host=host_parts[0],
                port=host_parts[1] if len(host_parts) > 1 else None,
                database=schema,
                query=options
            )
            return sa_create_engine(url, *args, **kwargs)

        elif ds_type == 7:  # PostgreSQL
            url = URL.create(
                drivername=self._driver or 'postgresql+psycopg2',
                username=conn_info.username,
                password=conn_info.password,
                host=host_parts[0],
                port=host_parts[1] if len(host_parts) > 1 else None,
                database=schema
            )
        elif ds_type == 1:  # ClickZetta
            if not conn_info.workspaceName or not conn_info.instanceName:
                raise DatabaseConnectionError("Missing required parameters 'workspace_name', "
                                              "'instance_name' for ClickZetta data source")
            if not self._vcluster:
                raise DatabaseConnectionError("Missing virtual cluster for ClickZetta data source")

            if conn_info.username and conn_info.password:
                base_url = (f"clickzetta://{conn_info.username}:{conn_info.password}@{conn_info.instanceName}."
                            f"{conn_info.host}/"
                            f"{conn_info.workspaceName}"
                            f"?virtualcluster={self._vcluster}"
                            )
            elif conn_info.magicToken:
                base_url = (f"clickzetta://{conn_info.instanceName}.{conn_info.host}/"
                            f"{conn_info.workspaceName}"
                            f"?magic_token={conn_info.magicToken}"
                            f"&virtualcluster={self._vcluster}"
                            )
            else:
                raise ValueError("username and password or token must be specified")


            # Add schema if provided
            if schema:
                base_url += f"&schema={schema}"

            url = base_url
        else:
            raise ValueError(f"Unsupported data source type: {ds_type}")

        return sa_create_engine(url, connect_args={'options': self._convert_options(options)}, *args, **kwargs)

    @staticmethod
    def _convert_options(options):
        if not options:
            return ''
        return ' '.join([f'-c {k}={v}' for k, v in options.items()])


def get_lakehouse_client(conn):
    return conn.connection.connection._client


def get_active_engine(
        ds_name: str,
        vcluster: Optional[str] = None,
        workspace: Optional[str] = None,
        schema: Optional[str] = None,
        options: Optional[Dict[str, str]] = None,
        *args, **kwargs
) -> Engine:
    """
    Convenience function to create a database engine.

    Args:
        ds_name (str): Data source name
        workspace (str, optional): Workspace name
        schema (str, optional): Schema name
        vcluster (str, optional): Virtual cluster name

    Returns:
        SQLAlchemy Engine instance
    """
    manager = DatabaseConnectionManager()

    if workspace:
        manager.use_workspace(workspace)
    if schema:
        manager.use_schema(schema)
    if vcluster:
        manager.use_vcluster(vcluster)
    if options:
        manager.use_options(options)

    return manager.connect(ds_name, *args, **kwargs)
