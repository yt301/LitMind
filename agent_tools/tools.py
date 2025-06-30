
# 格式化用户输入为json格式
def gain_userinput(userinput,source_language,translated_language,style):
    return {
        "text": f"{userinput}",
        "source_language": f"{source_language}",
        "translated_language": f"{translated_language}",
        "style": f"{style}",
    }