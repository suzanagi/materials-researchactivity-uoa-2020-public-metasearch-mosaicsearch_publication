class TestUtils:
  @staticmethod
  # Returns the list of titles obtained from the given list of search results
  def get_title_list_from(result_list: list) -> list:
    titles = []
    for item in result_list:
      titles.append(item.get_title())
    return titles

  @staticmethod
  def get_url_list_from(result_list: list) -> list:
    urls = []
    for item in result_list:
      urls.append(item.get_url())
    return urls

  @staticmethod
  def get_str_expression_list_from(result_list: list) -> list:
    str_expressions = []
    for item in result_list:
      str_expressions.append(str(item))
    return str_expressions

  @staticmethod
  def print_search_result_item_list(items_list: list) -> list:
    for i in range(0, len(items_list)):
      print("[", i, "] ", items_list[i])