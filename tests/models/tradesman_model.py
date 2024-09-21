from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class ContentTypeBase(BaseModel):
    id: Optional[int]
    app_label: str
    model: str

    class Config:
        from_attributes = True

class PermissionBase(BaseModel):
    id: Optional[int]
    name: str
    content_type: Optional[ContentTypeBase]
    codename: str

    class Config:
        from_attributes = True

class GroupBase(BaseModel):
    id: Optional[int]
    name: str
    permissions: List[PermissionBase]

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    id: Optional[int]
    password: str
    last_login: Optional[datetime]
    is_superuser: bool
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    is_staff: bool
    is_active: bool
    date_joined: datetime
    groups: List[GroupBase]
    user_permissions: List[PermissionBase]

    class Config:
        from_attributes = True

class LogEntryBase(BaseModel):
    id: Optional[int]
    action_time: datetime
    user: Optional[UserBase]
    content_type: Optional[ContentTypeBase]
    object_id: Optional[str]
    object_repr: str
    action_flag: Any
    change_message: Optional[str]

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    session_key: str
    session_data: str
    expire_date: datetime

    class Config:
        from_attributes = True

class SiteBase(BaseModel):
    id: Optional[int]
    domain: str
    name: str

    class Config:
        from_attributes = True

class FacilityBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    name: str
    internal_id: str
    slug: Optional[Any]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class LocationBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    name: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class UserLocationBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    user: Optional[UserBase]
    location: Optional[LocationBase]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    user: Optional[UserBase]
    role: str
    pin: Optional[str]
    mfa_valid_till_datetime: datetime
    eula_agreement_signed: bool
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    competency_assignments: Optional[Any]

    class Config:
        from_attributes = True

class MfaCodeBase(BaseModel):
    id: Optional[int]
    user: Optional[UserBase]
    code: str
    expiration_datetime: datetime

    class Config:
        from_attributes = True

class SystemConfigurationBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    management_staff_timeout: Any
    power_user_staff_timeout: Any
    floor_staff_timeout: Any
    verified_ip_list: Any
    verified_device_list: Any
    active_device_list: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class FacilityUserBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    user: Optional[UserBase]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ZoneBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    parent: Optional['ZoneBase']
    facility: Optional[FacilityBase]
    name: str
    internal_id: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductionLineBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    name: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class AssetBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    production_line: Optional[ProductionLineBase]
    name: str
    description: Optional[str]
    internal_id: str
    type: str
    serial_number: Optional[str]
    manufacturer: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    competency_assignments: Optional[Any]

    class Config:
        from_attributes = True

class AssetStatusBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    asset: Optional[AssetBase]
    status: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class AssetContactBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    asset: Optional[AssetBase]
    relationship: Optional[str]
    name: str
    email: str
    phone_number: Optional[str]
    company: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class PartBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    name: str
    code: Optional[str]
    description: Optional[str]
    quantity: int
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class AssetPartBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    asset: Optional[AssetBase]
    part: Optional[PartBase]
    quantity: int
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class DataChartBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    name: str
    interval: str
    calculation_type: str
    include_trend_line: bool
    statistic_name_list: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class DataChartKPIBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    data_chart: Optional[DataChartBase]
    name: str
    value: int
    line_color_rgba: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    content_type: Optional[ContentTypeBase]
    object_id: Any
    parent: Optional['CommentBase']
    user: Optional[UserBase]
    information: str
    created_datetime: datetime
    is_edited: bool
    content_object: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class FileBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    content_type: Optional[ContentTypeBase]
    object_id: Optional[Any]
    file: Any
    name: str
    type: str
    size: str
    related_field: Optional[str]
    content_object: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    email: str
    name: Optional[str]
    title: str
    body: str
    url: str
    send_datetime: datetime
    created_datetime: datetime
    sent_datetime: Optional[datetime]
    is_sent: bool

    class Config:
        from_attributes = True

class RecurrenceBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    content_type: Optional[ContentTypeBase]
    object_id: Optional[Any]
    recurrence_type: str
    start_date: date
    end_date: Optional[date]
    run_every: int
    selected_days: Any
    day_of_month: Optional[int]
    monthly_recurrence_type: str
    next_run_date: date
    content_object: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class DataCategoryBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    name: str

    class Config:
        from_attributes = True

class DataCategoryGroupBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    category: Optional[DataCategoryBase]
    name: str
    added_datetime: datetime
    updated_datetime: datetime
    reference_date: date

    class Config:
        from_attributes = True

class DataStatisticBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    category: Optional[DataCategoryBase]
    category_group: Optional[DataCategoryGroupBase]
    name: str
    type: str
    value_decimal: Optional[Decimal]
    value_int: Optional[int]
    value_json: Optional[Any]
    interval_type: str
    order: int
    added_datetime: datetime
    updated_datetime: datetime
    reference_date: date

    class Config:
        from_attributes = True

class MaintenanceBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    name: str

    class Config:
        from_attributes = True

class ProductionBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    name: str

    class Config:
        from_attributes = True

class SignageBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    name: str

    class Config:
        from_attributes = True

class WarehouseBase(BaseModel):
    id: Optional[int]
    facility: Optional[FacilityBase]
    name: str

    class Config:
        from_attributes = True

class BomBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    product_code: str
    created_datetime: datetime
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class BomCostBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    bom: Optional[BomBase]
    cost: float
    created_datetime: datetime
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductCodeStructureBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    name: str
    code: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductCodeStructureSegmentBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    code_structure: Optional[ProductCodeStructureBase]
    name: str
    separator: Optional[str]
    length: Any
    order: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductCodeCategoryBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    code_structure: Optional[ProductCodeStructureBase]
    name: str
    code: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductCodeCategoryQuestionChoicesBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    name: str
    values: Any
    codes: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductCodeCategoryQuestionBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    category: Optional[ProductCodeCategoryBase]
    order: Any
    label: str
    field_name: str
    field_type: str
    choices: Optional[ProductCodeCategoryQuestionChoicesBase]
    max_length: Optional[Any]
    min_length: Optional[Any]
    segment_name: Optional[str]
    is_required: bool
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    requestor: Optional[UserBase]
    submitter: Optional[UserBase]
    owner: Optional[UserBase]
    name: str
    category: str
    status: str
    phase: Optional[str]
    location: str
    department: str
    priority: str
    work_type: Optional[str]
    completed_date: Optional[date]
    required_date: date
    estimated_start_date: Optional[date]
    estimated_completion_date: Optional[date]
    estimated_effort: Optional[float]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringRequestStatusTrackingBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    engineering_request: Optional[EngineeringRequestBase]
    user: Optional[UserBase]
    status: str
    phase: Optional[str]
    description: str
    reference_datetime: datetime
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringAutomationRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    request: Optional[EngineeringRequestBase]
    type: str
    description: Optional[str]
    reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    tasks: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringDocumentationRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    request: Optional[EngineeringRequestBase]
    type: str
    description: Optional[str]
    reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    tasks: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringEquipmentRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    request: Optional[EngineeringRequestBase]
    type: str
    description: str
    reason: Optional[str]
    asset: Optional[str]
    product_code: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    tasks: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringGeneralDrawingRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    request: Optional[EngineeringRequestBase]
    type: str
    description: Optional[str]
    reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    tasks: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringOtherRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    request: Optional[EngineeringRequestBase]
    type: str
    description: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    tasks: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringProductRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    request: Optional[EngineeringRequestBase]
    type: str
    product_code: str
    sales_forecast: Optional[str]
    order_number: Optional[int]
    mo_number: Optional[int]
    description: Optional[str]
    reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    tasks: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class EngineeringProcessRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    request: Optional[EngineeringRequestBase]
    type: str
    description: str
    reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    tasks: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class ActivityLogBase(BaseModel):
    id: Optional[int]
    content_type: Optional[ContentTypeBase]
    object_id: Any
    user: Optional[UserBase]
    recipient: Optional[UserBase]
    device: Optional[str]
    created_datetime: datetime
    verb: str
    information: Optional[str]
    content_object: Any

    class Config:
        from_attributes = True

class ActivitySubscriberBase(BaseModel):
    id: Optional[int]
    activity: Optional[ActivityLogBase]
    subscriber: Optional[UserBase]

    class Config:
        from_attributes = True

class EventHistoryBase(BaseModel):
    id: Optional[int]
    content_type: Optional[ContentTypeBase]
    object_id: Any
    created_datetime: datetime
    event: str
    content_object: Any

    class Config:
        from_attributes = True

class ViewBase(BaseModel):
    id: Optional[int]
    content_type: Optional[ContentTypeBase]
    object_id: Any
    user: Optional[UserBase]
    created_datetime: datetime
    content_object: Any

    class Config:
        from_attributes = True

class CompetencyBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    name: str
    description: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CompetencyLevelBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    competency: Optional[CompetencyBase]
    name: str
    level: Any
    description: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CompetencyLevelAssignmentBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    content_type: Optional[ContentTypeBase]
    object_id: Any
    level: Optional[CompetencyLevelBase]
    content_object: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SeiInventoryBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    product_code: str
    description: str
    on_hand: int
    inventory_data: Any
    product_account_set_code: Optional[str]
    default_picking_sequence: Optional[str]
    product_area: Optional[str]
    bag_quantity: int
    carton_quantity: int
    skid_quantity: int
    unit_of_measure: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SeiInventoryLocationBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    code: str
    name: str
    name_long: str
    address_1: Optional[str]
    address_2: Optional[str]
    address_3: Optional[str]
    address_4: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip: Optional[str]
    phone: Optional[str]
    contact: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CoilBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    po_number: str
    product_code: str
    decimal_gauge: Decimal
    width_inches: Decimal
    tag_number: str
    receipt_number: Optional[str]
    vendor: str
    notes: Optional[str]
    status: str
    unique_code: str
    stage: str
    created_datetime: datetime
    updated_datetime: datetime
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CoilWeightBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    coil: Optional[CoilBase]
    pounds: Decimal
    created_datetime: datetime
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CoilLocationBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    coil: Optional[CoilBase]
    location: Optional[SeiInventoryLocationBase]
    type: str
    transferred_datetime: datetime
    created_datetime: datetime
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SeiCoilPropertyBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    item_number: str
    property_id: Optional[str]
    property_id_2: Optional[str]
    description: Optional[str]
    metal_coating: Optional[str]
    metal_specification: Optional[str]
    metal_comment_1: Optional[str]
    metal_comment_2: Optional[str]
    metal_use: Optional[str]
    max_outside_diameter: Optional[Decimal]
    optimal_outside_diameter: Optional[Decimal]
    optimal_weight: Optional[Decimal]
    thickness: Optional[Decimal]
    thickness_tolerance: Optional[Decimal]
    width: Optional[Decimal]
    width_tolerance_negative: Optional[Decimal]
    width_tolerance_positive: Optional[Decimal]
    tolerance_specification: Optional[str]
    tolerance_type: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CoilCycleCountBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    location: Optional[SeiInventoryLocationBase]
    scanned: Any
    not_scanned: Any
    completed_scanned: Any
    without_receipt_number: Any
    missing_coil_unique_codes: Any
    status: str
    created_datetime: datetime
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CoilFloorRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    requestor: Optional[UserBase]
    approver: Optional[UserBase]
    deliverer: Optional[UserBase]
    completer: Optional[UserBase]
    canceller: Optional[UserBase]
    deliver_to: str
    phase: str
    required_by_date: date
    requested_datetime: datetime
    approved_datetime: Optional[datetime]
    delivered_datetime: Optional[datetime]
    cancelled_datetime: Optional[datetime]
    completed_datetime: Optional[datetime]
    is_short_notice: bool
    short_notice_reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class CoilFloorRequestItemBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    coil_floor_request: Optional[CoilFloorRequestBase]
    status: str
    product_code: str
    requested_weight: Decimal
    actual_weight: Optional[Decimal]
    comment: Optional[str]
    feedback: Optional[str]
    required_by_time: Any
    delivery_datetime: Optional[datetime]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class InventoryAdjustmentRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    requestor: Optional[UserBase]
    documentor: Optional[UserBase]
    approver: Optional[UserBase]
    completer: Optional[UserBase]
    canceller: Optional[UserBase]
    phase: str
    document_number: Optional[str]
    comment: Optional[str]
    requested_datetime: datetime
    document_number_entered_datetime: Optional[datetime]
    approved_datetime: Optional[datetime]
    completed_datetime: Optional[datetime]
    cancelled_datetime: Optional[datetime]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class InventoryAdjustmentRequestItemBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    inventory_adjustment_request: Optional[InventoryAdjustmentRequestBase]
    status: str
    product_code: str
    sage_location: str
    unit_of_measure: str
    comment: Optional[str]
    reason: str
    value_change_type: Optional[str]
    value: Decimal
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class BlankInventoryFloorRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    requestor: Optional[UserBase]
    approver: Optional[UserBase]
    delivering: Optional[UserBase]
    deliverer: Optional[UserBase]
    completer: Optional[UserBase]
    canceller: Optional[UserBase]
    location: Optional[LocationBase]
    deliver_to: str
    phase: str
    required_by_date: date
    requested_datetime: datetime
    approved_datetime: Optional[datetime]
    delivering_datetime: Optional[datetime]
    delivered_datetime: Optional[datetime]
    cancelled_datetime: Optional[datetime]
    completed_datetime: Optional[datetime]
    is_short_notice: bool
    short_notice_reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class BlankInventoryFloorRequestItemBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    blank_inventory_request: Optional[BlankInventoryFloorRequestBase]
    status: str
    product_code: str
    description: str
    requested_quantity: int
    required_by_time: Any
    comment: Optional[str]
    document_number: Optional[str]
    actual_quantity: int
    feedback: Optional[str]
    delivery_datetime: Optional[datetime]
    paperwork_datetime: Optional[datetime]
    is_staged: bool
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SeiBlankInventoryItemBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    product_code: str
    description: str
    on_hand: int
    inventory_data: Any
    product_account_set_code: Optional[str]
    default_picking_sequence: Optional[str]
    product_area: Optional[str]
    bag_quantity: int
    carton_quantity: int
    skid_quantity: int
    unit_of_measure: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class NonMfgInventoryFloorRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    user: Optional[UserBase]
    manager: Optional[UserBase]
    processor: Optional[UserBase]
    completer: Optional[UserBase]
    canceller: Optional[UserBase]
    location: Optional[LocationBase]
    document_number: Optional[str]
    phase: str
    required_by_date: date
    approval_datetime: Optional[datetime]
    processing_datetime: Optional[datetime]
    cancelled_datetime: Optional[datetime]
    completed_datetime: Optional[datetime]
    requested_datetime: datetime
    rejected_datetime: Optional[datetime]
    is_short_notice: bool
    short_notice_reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SeiNonMfgInventoryItemBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    product_code: str
    description: str
    on_hand: int
    inventory_data: Any
    product_account_set_code: Optional[str]
    default_picking_sequence: Optional[str]
    product_area: Optional[str]
    bag_quantity: int
    carton_quantity: int
    skid_quantity: int
    unit_of_measure: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class NonMfgInventoryFloorRequestItemBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    inventory_request: Optional[NonMfgInventoryFloorRequestBase]
    inventory_item: Optional[SeiNonMfgInventoryItemBase]
    requested_quantity: Any
    comment: Optional[str]
    feedback: str
    status: str
    transfer_type: str
    actual_quantity: Any
    processing_notes: str
    is_picked: bool
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SeiProductCodeBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    watchdog_key: Optional[str]
    code: str
    formatted_code: str
    category: str
    stock_unit: str
    unit_weight: Decimal
    picking_sequence: str
    description: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class NonMfgCodeRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    facility: Optional[FacilityBase]
    type: str
    name: Optional[str]
    code: Optional[str]
    description: str
    use_case: Optional[str]
    link_to_website: Optional[Any]
    similar_sage_product_code: Optional[str]
    vendor_name: Optional[str]
    vendor_pricing: Optional[Decimal]
    storage_location: Optional[str]
    max_stock_quantity: Optional[int]
    carton_quantity: Optional[int]
    unit_of_measure: Optional[str]
    status: str
    notes: Optional[str]
    processing_tasks: Any
    requestor: Optional[UserBase]
    manager: Optional[UserBase]
    created_datetime: datetime
    approved_datetime: Optional[datetime]
    resubmitted_datetime: Optional[datetime]
    revise_datetime: Optional[datetime]
    rejected_datetime: Optional[datetime]
    cancelled_datetime: Optional[datetime]
    completed_datetime: Optional[datetime]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    name: str
    description: str
    estimated_hours: Decimal
    category: str
    target_type: str
    service_type: str
    priority: str
    asset: Optional[AssetBase]
    status: str
    due_date: date
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    files: Optional[Any]
    competency_assignments: Optional[Any]
    comments: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderDueDateTrackingBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    work_order: Optional[WorkOrderBase]
    user: Optional[UserBase]
    due_datetime: date
    reason: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderStatusTrackingBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    work_order: Optional[WorkOrderBase]
    user: Optional[UserBase]
    status: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderPartBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    work_order: Optional[WorkOrderBase]
    part: Optional[PartBase]
    quantity: int
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderRequestBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    asset: Optional[AssetBase]
    requestor: Optional[UserBase]
    name: str
    description_of_issue: str
    urgency: str
    reason_for_urgency: str
    lock_out: Optional[str]
    report_machine_down: bool
    status: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderRequestStatusTrackingBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    work_order_request: Optional[WorkOrderRequestBase]
    status: str
    user: Optional[UserBase]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    comments: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderSchedulerBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    asset: Optional[AssetBase]
    work_order: Optional[WorkOrderBase]
    trigger_type: str
    days_to_complete: int
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SchedulerDateTriggerBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    scheduler: Optional[WorkOrderSchedulerBase]
    has_triggered: bool
    trigger_datetime: Optional[date]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    recurrences: Optional[Any]

    class Config:
        from_attributes = True

class SchedulerCycleTriggerBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    scheduler: Optional[WorkOrderSchedulerBase]
    has_triggered: bool
    cycle_type: str
    cycle_recurrence_amount: Optional[int]
    cycle_trigger_amount: int
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    recurrences: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderTaskBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    work_order: Optional[WorkOrderBase]
    name: str
    description: Optional[str]
    status: str
    order: Any
    completer: Optional[UserBase]
    completed_datetime: Optional[datetime]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    files: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderTimeClockBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    work_order: Optional[WorkOrderBase]
    user: Optional[UserBase]
    status: str
    start_datetime: datetime
    end_datetime: Optional[datetime]
    total_seconds: int
    is_running: bool
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class WorkOrderUserBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    work_order: Optional[WorkOrderBase]
    user: Optional[UserBase]
    role: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductClaimBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    reference_id: str
    customer_name: str
    company_name: str
    comment: Optional[str]
    email: str
    inventory_adjustment_number: Optional[str]
    phone_number: str
    po_number: Optional[str]
    reason_for_claim: Optional[Any]
    product_received_date: date
    shipper: str
    submission_date: date
    signature: str
    uuid: Any
    status: str
    reason_kpi: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductClaimItemBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    product_claim: Optional[ProductClaimBase]
    item: Optional[str]
    shipment_number: Optional[str]
    reason: Optional[str]
    quantity_billed: Optional[Any]
    quantity_received: Optional[Any]
    quantity_damaged: Optional[Any]
    quoted_price: Optional[float]
    price_charged: Optional[float]
    product_back_order: bool
    quality_control_label_date: Optional[date]
    images: Optional[Any]
    status: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductClaimStatusTrackingBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    product_claim: Optional[ProductClaimBase]
    user: Optional[UserBase]
    status: str
    description: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductClaimRawDataBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    data: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductClaimDepartmentBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    product_claim: Optional[ProductClaimBase]
    owner: Optional[UserBase]
    department: str
    action_taken_by: Optional[UserBase]
    action_taken: bool
    action_taken_datetime: Optional[datetime]
    description: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class AccountsReceivableProductClaimBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    claim: Optional[ProductClaimDepartmentBase]
    description: Optional[str]
    action: Optional[str]
    debit_credit_number: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductionProductClaimBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    claim: Optional[ProductClaimDepartmentBase]
    description: Optional[str]
    action: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class SalesProductClaimBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    claim: Optional[ProductClaimDepartmentBase]
    description: Optional[str]
    action: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class WarehouseProductClaimBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    claim: Optional[ProductClaimDepartmentBase]
    description: Optional[str]
    action: Optional[str]
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class ProductClaimInteractionBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    product_claim: Optional[ProductClaimBase]
    user: Optional[UserBase]
    date: date
    type: str
    description: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    content_type: Optional[ContentTypeBase]
    object_id: Optional[Any]
    parent: Optional['TaskBase']
    name: str
    description: Optional[str]
    hours: Decimal
    required_by_date: date
    status: str
    priority: str
    content_object: Any
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]
    comments: Optional[Any]

    class Config:
        from_attributes = True

class TaskUserBase(BaseModel):
    id: Optional[int]
    is_active: bool
    is_deleted: bool
    created_datetime: Optional[datetime]
    facility: Optional[FacilityBase]
    user: Optional[UserBase]
    task: Optional[TaskBase]
    role: str
    activities: Optional[Any]
    event_history: Optional[Any]
    views: Optional[Any]
    activity_log: Optional[Any]

    class Config:
        from_attributes = True


CONTENT_TYPE_MAP = {
    'LogEntry': 1,
    'Permission': 2,
    'Group': 3,
    'User': 4,
    'ContentType': 5,
    'Session': 6,
    'Site': 7,
    'UserLocation': 8,
    'UserProfile': 9,
    'MfaCode': 10,
    'SystemConfiguration': 11,
    'Facility': 68,
    'FacilityUser': 69,
    'Zone': 70,
    'Asset': 105,
    'AssetStatus': 104,
    'AssetContact': 167,
    'AssetPart': 106,
    'DataChart': 12,
    'DataChartKPI': 13,
    'Comment': 14,
    'File': 15,
    'Notification': 16,
    'Recurrence': 140,
    'DataCategory': 17,
    'DataCategoryGroup': 22,
    'DataStatistic': 23,
    'Maintenance': 17,
    'Production': 17,
    'Signage': 17,
    'Warehouse': 17,
    'Bom': 24,
    'BomCost': 25,
    'ProductCodeStructure': 34,
    'ProductCodeStructureSegment': 36,
    'ProductCodeCategory': 32,
    'ProductCodeCategoryQuestion': 35,
    'ProductCodeCategoryQuestionChoices': 33,
    'EngineeringRequest': 63,
    'EngineeringRequestStatusTracking': 67,
    'EngineeringAutomationRequest': 127,
    'EngineeringDocumentationRequest': 128,
    'EngineeringEquipmentRequest': 129,
    'EngineeringGeneralDrawingRequest': 130,
    'EngineeringOtherRequest': 131,
    'EngineeringProductRequest': 133,
    'EngineeringProcessRequest': 132,
    'ActivityLog': 37,
    'ActivitySubscriber': 38,
    'EventHistory': 39,
    'View': 40,
    'Competency': 110,
    'CompetencyLevel': 109,
    'CompetencyLevelAssignment': 111,
    'SeiInventory': 41,
    'SeiInventoryLocation': 42,
    'Coil': 43,
    'CoilWeight': 46,
    'CoilLocation': 45,
    'SeiCoilProperty': 44,
    'CoilCycleCount': 47,
    'CoilFloorRequest': 48,
    'CoilFloorRequestItem': 49,
    'InventoryAdjustmentRequest': 50,
    'InventoryAdjustmentRequestItem': 51,
    'Part': 113,
    'BlankInventoryFloorRequest': 53,
    'BlankInventoryFloorRequestItem': 54,
    'SeiBlankInventoryItem': 41,
    'NonMfgInventoryFloorRequest': 56,
    'NonMfgInventoryFloorRequestItem': 57,
    'SeiNonMfgInventoryItem': 41,
    'SeiProductCode': 58,
    'NonMfgCodeRequest': 59,
    'Location': 60,
    'WorkOrder': 117,
    'WorkOrderDueDateTracking': 137,
    'WorkOrderStatusTracking': 138,
    'WorkOrderPart': 134,
    'WorkOrderRequest': 119,
    'WorkOrderRequestStatusTracking': 121,
    'WorkOrderScheduler': 154,
    'SchedulerDateTrigger': 156,
    'SchedulerCycleTrigger': 157,
    'WorkOrderTask': 139,
    'WorkOrderTimeClock': 136,
    'WorkOrderUser': 135,
    'ProductClaim': 145,
    'ProductClaimItem': 144,
    'ProductClaimStatusTracking': 146,
    'ProductClaimRawData': 166,
    'ProductClaimDepartment': 165,
    'AccountsReceivableProductClaim': 161,
    'ProductionProductClaim': 163,
    'SalesProductClaim': 160,
    'WarehouseProductClaim': 162,
    'ProductClaimInteraction': 159,
    'ProductionLine': 108,
    'Task': 61,
    'TaskUser': 62,
}
