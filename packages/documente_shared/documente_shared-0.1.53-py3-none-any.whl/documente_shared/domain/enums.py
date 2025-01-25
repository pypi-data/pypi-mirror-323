from documente_shared.domain.base_enum import BaseEnum


class DocumentProcessingStatus(BaseEnum):
    PENDING = 'PENDING'
    ENQUEUED = 'ENQUEUED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    DELETED = 'DELETED'
    CANCELLED = 'CANCELLED'
    IN_REVIEW = 'IN_REVIEW'

class DocumentProcessingCategory(BaseEnum):
    CIRCULAR = 'CIRCULAR'
    DESGRAVAMEN = 'DESGRAVAMEN'

    @property
    def is_circular(self):
        return self == DocumentProcessingCategory.CIRCULAR

    @property
    def is_desgravamen(self):
        return self == DocumentProcessingCategory.DESGRAVAMEN


class DocumentProcessingSubCategory(BaseEnum):
    # Circulares
    CC_COMBINADA = 'CC_COMBINADA'
    CC_NORMATIVA = 'CC_NORMATIVA'
    CC_INFORMATIVA = 'CC_INFORMATIVA'
    CC_RETENCION_SUSPENSION_REMISION = 'CC_RETENCION_SUSPENSION_REMISION'

    # Desgravamenes
    DS_CREDISEGURO = 'DS_CREDISEGURO'

