from django.test import TestCase
from metasearch.models import ResultItem
from metasearch.views import (
  dump_log,
  push_into_json,
  make_metasearch_process_log_text,
  stringify_result_items_list_for_logging,
  stringify_result_items_dict_for_logging
)

class DevelopmentUtilitiesTests(TestCase):
  
  def test_push_into_json_works_correctly(self):
    # arguments given to the function
    arguments_to_be_given = (
      ("argument 1 title", "argument 1 content"),
      ("argument 2 title", "argument 2 content")
    )
    # expected result
    expected: str = "{\"argument 1 title\": \"argument 1 content\", \"argument 2 title\": \"argument 2 content\"}"
    # actual result
    actual: str = push_into_json(("argument 1 title", "argument 1 content"), ("argument 2 title", "argument 2 content"))
    # assertion
    self.assertEqual(expected, actual)

  def test_dump_log_works_correctly(self):
    # name of the file opened in this test
    f_name: str = "test_dump_log_works_correctly_sample_dump_file"
    # header message
    message: str = "sample message"

    ''' test set 1 : in case of list '''
    sample_result_items: list = [
      ResultItem("Article 1", "http://www.example1.com/example", "Google", 1),
      ResultItem("Article 2", "http://www.example2.com", "Yahoo!", 2),
      ResultItem("Article 3", "https://example3.org", "Bing", 3)
    ]
    dump_log(f_name, message, sample_result_items)
    expected_content = message
    for item in sample_result_items:
      expected_content = expected_content+'\n'+str(item)
    actual_content = ""
    with open('./metasearch/log_files/'+f_name+'.txt') as f:
      actual_content = f.read()
    self.assertEqual(expected_content, actual_content)

    ''' test set 2 : in case of dict '''
    sample_result_items: dict = {
      "group 1": [ResultItem("Article 1", "http://www.example1.com/example", "Google", 1)],
      "group 2": [
        ResultItem("Article 2", "http://www.example2.com", "Yahoo!", 2),
        ResultItem("Article 3", "https://example3.org", "Bing", 3)
      ]
    }
    dump_log(f_name, message, sample_result_items)
    expected_content = message
    expected_content = expected_content + '\n' + "<<group 1>>"
    expected_content = expected_content + '\n' + str(sample_result_items["group 1"][0])
    expected_content = expected_content + '\n' + "<<group 2>>"
    expected_content = expected_content + '\n' + str(sample_result_items["group 2"][0])
    expected_content = expected_content + '\n' + str(sample_result_items["group 2"][1])
    actual_content = ""
    with open('./metasearch/log_files/'+f_name+'.txt') as f:
      actual_content = f.read()
    self.assertEqual(expected_content, actual_content)

  def test_stringify_result_items_list_for_logging(self):
    results_to_be_dumped: list = []
    results_to_be_dumped.append(ResultItem("result item title 1", "https://urlfortesting1.com", "Google", 1))
    results_to_be_dumped.append(ResultItem("result item title 2", "https://urlfortesting2.com", "Yahoo!", 9))
    expected_text: str = str(results_to_be_dumped[0]) + '\n' + str(results_to_be_dumped[1]) + '\n'
    actual_text: str = stringify_result_items_list_for_logging(results_to_be_dumped)
    self.assertEqual(expected_text, actual_text)

  def test_stringify_result_items_dict_for_logging(self):
    results_to_be_dumped: dict = {}
    results_list: list = []
    results_list.append(ResultItem("result item title 1", "https://urlfortesting1.com", "Google", 1))
    results_list.append(ResultItem("result item title 2", "https://urlfortesting2.com", "Yahoo!", 9))
    results_to_be_dumped[1] = results_list
    expected_text: str = "<<< 1 >>>\n" + str(results_list[0]) + '\n' + str(results_list[1]) + '\n' + '\n'
    actual_text: str = stringify_result_items_dict_for_logging(results_to_be_dumped)
    self.assertEqual(expected_text, actual_text)