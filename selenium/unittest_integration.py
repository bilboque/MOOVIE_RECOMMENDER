import subprocess
import unittest


class RunScriptsTest(unittest.TestCase):

    def run_script(self, script):
        print(f"Running script: {script}")
        result = subprocess.run(
            ['python', script], capture_output=True, text=True)

        # Check the exit code of the subprocess
        if result.returncode != 0:
            print(f"Error occurred while running {script}:")
            print(result.stderr)

        # Assert that the script did not finish with an error
        self.assertEqual(result.returncode, 0,
                         f"Script {script} finished with an error.")

    def test_login(self):
        self.run_script('./login.py')

    def test_advanced(self):
        self.run_script('./advanced.py')

    def test_classic(self):
        self.run_script('./classic_search.py')

    def test_redirect(self):
        self.run_script('./login_redirect.py')

    # Add more test methods for other scripts if needed


if __name__ == "__main__":
    unittest.main()
