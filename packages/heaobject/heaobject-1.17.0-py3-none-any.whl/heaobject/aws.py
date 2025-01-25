"""
Utility classes and functions for working with AWS.
"""
import abc
from heaobject import root
from typing import Literal, Optional
import re


class S3StorageClass(root.EnumWithAttrs):
    """
    The S3 storage classes. The list of storage classes is documented at
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2, and
    each storage class is explained in detail at
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html.
    """
    def __init__(self, display_name: str):
        self.__display_name = display_name

    @property
    def display_name(self) -> str:
        return self.__display_name

    STANDARD = 'Standard'
    DEEP_ARCHIVE = 'Glacier Deep Archive'
    GLACIER = 'Glacier Flexible Retrieval'
    GLACIER_IR = 'Glacier Instant Retrieval'
    REDUCED_REDUNDANCY = 'Reduced Redundancy'
    ONEZONE_IA = 'One Zone-IA'
    STANDARD_IA = 'Standard-IA'
    INTELLIGENT_TIERING = 'Intelligent Tiering'
    OUTPOSTS = 'Outposts'



def s3_uri(bucket: str | None, key: str | None = None) -> str | None:
    """
    Creates and returns a S3 URI from the given bucket and key.

    :param bucket: a bucket name (optional).
    :param key: a key (optional).
    :return: None if the bucket is None, else a S3 URI string.
    """
    if not bucket:
        return None
    return f"s3://{bucket}/{key if key is not None else ''}"


S3_URI_PATTERN = re.compile(r's3://(?P<bucket>[^/]+?)/(?P<key>.+)')
S3_URI_BUCKET_PATTERN = re.compile(r's3://(?P<bucket>[^/]+?)/')


class S3StorageClassMixin:
    """
    Mixin for adding a storage class property to a desktop object.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__storage_class: S3StorageClass | None = None

    @property
    def storage_class(self) -> S3StorageClass | None:
        """The AWS S3 storage class of this file."""
        return self.__storage_class

    @storage_class.setter
    def storage_class(self, storage_class: S3StorageClass | None):
        if storage_class is None:
            self.__storage_class = None
        elif isinstance(storage_class, S3StorageClass):
            self.__storage_class = storage_class
        else:
            try:
                self.__storage_class = S3StorageClass[str(storage_class)]
            except KeyError:
                raise ValueError(f'Invalid storage class {storage_class}')

    def set_storage_class_from_str(self, storage_class: Optional[str]):
        """
        Sets the storage class property to the storage class corresponding to the provided string.
        """
        if storage_class is None:
            self.__storage_class = None
        else:
            try:
                self.__storage_class = S3StorageClass[str(storage_class)]
            except KeyError:
                raise ValueError(f'Invalid storage class {storage_class}')


class S3Version(root.Version, S3StorageClassMixin):
    """
    Version information for S3 objects.
    """
    pass


class AWSDesktopObject(root.DesktopObject, abc.ABC):
    """
    Marker interface for AWS object classes, such as
    heaobject.folder.AWSS3Folder and heaobject.data.AWSS3FileObject.
    """
    pass


class S3Object(AWSDesktopObject, abc.ABC):
    """
    Marker interface for S3 object classes, such as
    heaobject.folder.AWSS3Folder and heaobject.data.AWSS3FileObject.
    """

    @property
    @abc.abstractmethod
    def key(self) -> Optional[str]:
        """
        The object's key.
        """
        pass

    @key.setter
    @abc.abstractmethod
    def key(self, key: Optional[str]):
        pass

    @property
    @abc.abstractmethod
    def s3_uri(self) -> Optional[str]:
        """
        The object's S3 URI, computed from the bucket id and the id field.
        """
        pass

    @property
    @abc.abstractmethod
    def bucket_id(self) -> Optional[str]:
        """
        The object's bucket name.
        """
        pass

    @bucket_id.setter
    @abc.abstractmethod
    def bucket_id(self, bucket_id: Optional[str]):
        pass


RegionLiteral = Literal['af-south-1', 'ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1',
                        'ap-south-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-3', 'ca-central-1',
                        'cn-north-1', 'cn-northwest-1', 'eu-central-1', 'eu-south-2', 'eu-north-1', 'eu-south-1',
                        'eu-west-1', 'eu-west-2', 'eu-west-3', 'me-south-1', 'sa-east-1', 'us-gov-east-1',
                        'us-gov-west-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'EU']


class S3EventName(root.EnumWithAttrs):
    def __init__(self, display_name: str):
        self.__display_name = display_name

    @property
    def display_name(self) -> str:
        return self.__display_name

    OBJECT_CREATED = "ObjectCreated"
    OBJECT_REMOVED = "ObjectRemoved"
    OBJECT_RESTORE = "ObjectRestore"

class S3EventNameMixin:
    """
    Mixin for adding a s3 event name property to a desktop object.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__event_name: S3EventName | None = None

    @property
    def event_name(self) -> S3EventName | None:
        """The AWS S3 storage class of this file."""
        return self.__event_name

    @event_name.setter
    def event_name(self, event_name: S3EventName | None):
        """

        :param event_name: event name is obtained from s3 event notification. For more details see
         https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-event-types-and-destinations.html
        :return:
        """
        if isinstance(event_name, S3EventName) or event_name is None:
            self.__event_name = event_name
        elif type(event_name) == str:
            if event_name and S3EventName.OBJECT_CREATED.display_name in event_name:
                self.__event_name = S3EventName.OBJECT_CREATED
            elif event_name and S3EventName.OBJECT_REMOVED.display_name in event_name:
                self.__event_name = S3EventName.OBJECT_REMOVED
            elif event_name and S3EventName.OBJECT_RESTORE.display_name in event_name:
                self.__event_name = S3EventName.OBJECT_RESTORE
            else:
                raise ValueError(f'Invalid event name {event_name}')
        else:
            raise ValueError(f'Invalid event name {event_name}')


class AmazonResourceName(root.AbstractMemberObject):
    """
    An Amazon Resource Name (ARN). ARNs are used to uniquely identify AWS resources.
    """
    def __init__(self) -> None:
        super().__init__()
        self.__partition = ''
        self.__service = ''
        self.__region = ''
        self.__account_id = ''
        self.__resource_type_and_id = ''

    @property
    def partition(self) -> str:
        return self.__partition

    @partition.setter
    def partition(self, partition: str):
        self.__partition = str(partition) if partition else ''

    @property
    def service(self) -> str:
        return self.__service

    @service.setter
    def service(self, service: str):
        self.__service = str(service) if service else ''

    @property
    def region(self) -> str:
        return self.__region

    @region.setter
    def region(self, region: str):
        self.__region = str(region) if region else ''

    @property
    def account_id(self) -> str:
        return self.__account_id

    @account_id.setter
    def account_id(self, account_id: str):
        self.__account_id = str(account_id) if account_id else ''

    @property
    def resource_type_and_id(self) -> str:
        return self.__resource_type_and_id

    @resource_type_and_id.setter
    def resource_type_and_id(self, resource_type_and_id: str):
        self.__resource_type_and_id = str(resource_type_and_id) if resource_type_and_id else ''

    def __iter__(self):
        return iter((self.partition, self.service, self.region, self.account_id, self.resource_type_and_id))

    def __getitem__(self, index: int):
        return (self.partition, self.service, self.region, self.account_id, self.resource_type_and_id)[index]

    def __str__(self) -> str:
        return f"arn:{self.partition}:{self.service}:{self.region}:{self.account_id}:{self.resource_type_and_id}"

    def to_arn_str(self) -> str:
        """
        Returns the ARN string representation of this ARN.
        """
        return str(self)

    @classmethod
    def from_arn_str(cls, arn: str) -> 'AmazonResourceName':
        """
        Extracts the partition, service, region, account ID, resource type, and resource ID from the given ARN.

        :param arn: an ARN string.
        """
        parts = arn.split(':', maxsplit=5)
        arn_ = AmazonResourceName()
        arn_.partition = parts[1]
        arn_.service = parts[2]
        arn_.region = parts[3]
        arn_.account_id = parts[4]
        arn_.resource_type_and_id = parts[5]
        return arn_
