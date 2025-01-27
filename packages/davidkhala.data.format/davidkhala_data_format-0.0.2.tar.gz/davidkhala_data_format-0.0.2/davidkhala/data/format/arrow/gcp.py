from davidkhala.gcp.auth import CredentialsInterface, ServiceAccountInfo
from davidkhala.gcp.auth.options import from_service_account, ServiceAccount
from pyarrow.fs import GcsFileSystem, FileInfo

from davidkhala.data.format.arrow.fs import FS


class GCS(FS):
    """
    https://arrow.apache.org/docs/python/generated/pyarrow.fs.GcsFileSystem.html
    - GcsFileSystem.open_append_stream(...) is not implemented.
        - > pyarrow.lib.ArrowNotImplementedError: Append is not supported in GCS
    """

    def __init__(self, public_bucket: bool = False, *, location='ASIA-EAST2', credentials: CredentialsInterface = None):
        options = {
            'anonymous': public_bucket,
            'default_bucket_location': location,
        }
        if credentials:
            options['access_token'] = credentials.token
            options['credential_token_expiration'] = credentials.expiry
        self.fs = GcsFileSystem(**options)

    @staticmethod
    def from_service_account(info: ServiceAccountInfo):
        service_account = from_service_account(info)
        ServiceAccount.token.fget(service_account)  # credential validation included
        return GCS(credentials=service_account.credentials)

    def ls(self, bucket: str) -> FileInfo | list[FileInfo]:
        return super().ls(bucket)

    def open_output_stream(self, path, **kwargs):
        if path.startswith('gs://'):
            path = path[5:]
        return super().open_output_stream(path)
