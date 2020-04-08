class Result:
    def __init__(self, success, value=None, message=None, exception=None):
        self.success = success
        self.value = value
        self.message = message
        self.exception = exception

    def __bool__(self):
        if self.value:
            return True

        return False

    def __call__(self):
        return self.value


if __name__ == '__main__':
    result = Result(True, "6969")

    if result.success:
        print(f"The result of testing 'result.success' is {result.value}.")

    if result:
        print("This should not print.")
