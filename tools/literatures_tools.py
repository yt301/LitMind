
# 比较model_in和数据库的model的信息是否完全相同
def is_equal(user, user_in):
    """
    :param user: Literature实例
    :param user_in: LiteratureIn实例-Pydantic 模型
    :return:相等返回True，否则False
    """
    user_in_dict = user_in.model_dump()  # 将 Pydantic 模型转换为字典
    # 遍历 user_out 的字段，并从 user 中提取对应的值
    for key in user_in_dict.keys():
        # 确保 user 有对应的字段
        if hasattr(user, key) and user_in_dict[key] != getattr(user, key):
            return False
    return True
