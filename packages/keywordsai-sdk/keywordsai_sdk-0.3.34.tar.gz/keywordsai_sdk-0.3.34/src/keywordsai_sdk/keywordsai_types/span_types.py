from keywordsai_sdk.keywordsai_types._internal_types import KeywordsAIBaseModel


class KeywordsAISpanAttributes:
    # Span attributes
    KEYWORDSAI_SPAN_CUSTOM_ID = "keywordsai.span_params.custom_identifier"

    # Customer params
    KEYWORDSAI_CUSTOMER_PARAMS_ID = "keywordsai.customer_params.customer_identifier"
    KEYWORDSAI_CUSTOMER_PARAMS_EMAIL = "keywordsai.customer_params.email"
    KEYWORDSAI_CUSTOMER_PARAMS_NAME = "keywordsai.customer_params.name"
    
    # Evaluation params
    KEYWORDSAI_EVALUATION_PARAMS_ID = "keywordsai.evaluation_params.evaluation_identifier"

    # Threads
    KEYWORDSAI_THREADS_ID = "keywordsai.threads.thread_identifier"

    # Metadata
    KEYWORDSAI_METADATA = "keywordsai.metadata" # This is a pattern, it can be  any "keywordsai.metadata.key" where key is customizable

