class LambdaConfig(object):
    def __init__(self, lambda_s3_bucket, lambda_s3_key, lambda_description, lambda_function_name, lambda_handler,
                 lambda_memory_size, lambda_role_arn, lambda_runtime, lambda_timeout):
        """
        Config object for lambda units
        :param lambda_s3_bucket: s3 bucket containing lambda function code
        :param lambda_s3_key: path and filename of lambda function code in s3 bucket
        :param lambda_description: description of lambda function
        :param lambda_function_name: lambda function name
        :param lambda_handler: entry method of lambda function code
        :param lambda_memory_size: memory size of lambd function, must be between 128 and 1536 and be multiple of 64
        :param lambda_role_arn: arn for iam role to run lambda as
        :param lambda_runtime: nodejs | nodejs4.3 | java8 | python2.7
        :param lambda_timeout: execution time at which Lambda should terminate the function. Minimum of 1.
        """
        self.lambda_s3_bucket = lambda_s3_bucket
        self.lambda_s3_key = lambda_s3_key
        self.lambda_description = lambda_description
        self.lambda_function_name = lambda_function_name
        self.lambda_handler = lambda_handler
        self.lambda_memory_size = lambda_memory_size
        self.lambda_role_arn = lambda_role_arn
        self.lambda_runtime = lambda_runtime
        self.lambda_timeout = lambda_timeout
