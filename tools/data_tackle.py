
# 将models转换为models_out的工具函数
def data_out(user, user_out):
    """
    :param user: models实例
    :param user_out: models_out实例
    :return:获取models中值后的models_out字典
    """
    user_out_dict = user_out.model_dump()  # 将 Pydantic 模型转换为字典
    # 遍历 user_out 的字段，并从 user 中提取对应的值
    for key in user_out_dict.keys():
        # 确保 user 有对应的字段
        if hasattr(user, key):
            user_out_dict[key] = getattr(user, key)
        else:
            # 如果 user 中没有该字段，可以选择抛出错误或忽略
            print(f"Warning: Field '{key}'from {user_out} not found in {user} object.")
    return user_out_dict  # 返回字典形式的用户输出数据