import pytest


# Global variables to override exit code
passed = 0
failed = 0
xfailed = 0
skipped = 0
xpassed = 0
error_setup = 0
error_teardown = 0


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Override exit code 0 and add exit code 6.
    Exit code 0: All tests are passed, xpassed or skipped and there were no errors.
    Exit code 6: No failed tests but there were xfailed tests or errors.
    """
    # print(f"\nExit status: {session.exitstatus}")
    global skipped, failed, xfailed, passed, xpassed, error_setup, error_teardown
    error = error_setup + error_teardown
    if failed + xfailed + error == 0:
        session.exitstatus = 0
    if xfailed + error > 0:
        session.exitstatus = 6
    # print(f"Exit status: {session.exitstatus}")
    # print(f"{failed} failed, {passed} passed, {skipped} skipped, {xfailed} xfailed, {xpassed} xpassed, {error} errors")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global skipped, failed, xfailed, passed, xpassed, error_setup, error_teardown
    outcome = yield
    report = outcome.get_result()
    # _debug(item, call, report)

    if call.when == 'setup':
        # For tests with the pytest.mark.skip fixture
        if report.skipped:
            skipped += 1
        # For setup fixture
        if report.failed and call.excinfo is not None:
            error_setup += 1

    if call.when == 'teardown':
        if report.failed and call.excinfo is not None:
            error_teardown += 1

    if report.when == 'call':
        xfail = hasattr(report, "wasxfail")
        if report.failed:
            failed += 1
        if report.skipped and not xfail:
            skipped += 1
        if report.skipped and xfail:
            xfailed += 1
        if report.passed and xfail:
            xpassed += 1
        if report.passed and not xfail:
            passed += 1


def _debug(item, call, report):
    print('\n')
    print("node: ", item.originalname)
    print("when: ", call.when)
    print("outcome: ", report.outcome)
    print("passed: ", report.passed)
    print("skipped: ", report.skipped)
    print("failed: ", report.failed)
    print("wasxfail: ", hasattr(report, "wasxfail"))
