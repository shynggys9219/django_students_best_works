import unittest
from coderunner import coderunner

#test for Python program
class TestRunB(unittest.TestCase):
	def test_run(self):
		program_name = "testfiles/" + "test_python.py"
		language = "Python"
		output = "testfiles/" + "output.txt"
		Input = "testfiles/" + "input.txt"
		r = coderunner.Run(program_name, language, output, Input)

		print(self.assertEqual(r.getStatus(),"Accepted", "Something Bota"))

		with open("result.txt", "w") as F:
			F.write(r.getOutput())


if __name__ == '__main__':
    unittest.main()
