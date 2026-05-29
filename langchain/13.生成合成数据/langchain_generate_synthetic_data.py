import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_experimental.tabular_synthetic_data.openai import (
    OPENAI_TEMPLATE,
    create_openai_data_generator,
)
from langchain_experimental.tabular_synthetic_data.prompts import (
    SYNTHETIC_FEW_SHOT_PREFIX,
    SYNTHETIC_FEW_SHOT_SUFFIX,
)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Dict,List,Any
from langchain_experimental.synthetic_data import (
    DatasetGenerator,
    create_data_generation_chain,
)
from langchain_classic.chains.openai_functions.extraction import create_extraction_chain_pydantic
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

# 医疗账单
class MedicalBilling(BaseModel):
    patient_id: int
    patient_name: str
    diagnosis_code: str
    procedure_code: str
    total_charge: float
    insurance_claim_amount: float

# 返回Dict格式的数据
def medical_sample_data() -> List[Dict[str, Any]]:
    examples = [
        {
            "example": """Patient ID: 123456, Patient Name: John Doe, Diagnosis Code: 
            J20.9, Procedure Code: 99203, Total Charge: $500, Insurance Claim Amount: $350"""
        },
        {
            "example": """Patient ID: 789012, Patient Name: Johnson Smith, Diagnosis 
            Code: M54.5, Procedure Code: 99213, Total Charge: $150, Insurance Claim Amount: $120"""
        },
        {
            "example": """Patient ID: 345678, Patient Name: Emily Stone, Diagnosis Code: 
            E11.9, Procedure Code: 99214, Total Charge: $300, Insurance Claim Amount: $250"""
        },
    ]

    return examples

# 提示词模板
def medical_prompt_template(examples):
    OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")

    prompt_template = FewShotPromptTemplate(
        prefix=SYNTHETIC_FEW_SHOT_PREFIX,
        examples=examples,
        suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
        input_variables=["subject", "extra"],
        example_prompt=OPENAI_TEMPLATE,
    )
    return prompt_template

def film_sample_data(model):
    inp = [
        {
            "Actor": "Tom Hanks",
            "Film": [
                "Forrest Gump",
                "Saving Private Ryan",
                "The Green Mile",
                "Toy Story",
                "Catch Me If You Can",
            ],
        },
        {
            "Actor": "Tom Hardy",
            "Film": [
                "Inception",
                "The Dark Knight Rises",
                "Mad Max: Fury Road",
                "The Revenant",
                "Dunkirk",
            ],
        },
    ]
    generator = DatasetGenerator(model, {"style": "informal", "minimal length": 500})
    dataset = generator(inp) # type: ignore
    return dataset,inp

class Actor(BaseModel):
    Actor: str = Field(description="name of an actor")
    Film: List[str] = Field(description="list of names of films they starred in")

try:
    model = ChatOpenAI(model=os.getenv("OPENAI_LLM_MODEL","gpt-4o-mini"), temperature=0.7)

    # medical_sample = medical_sample_data()
    # medical_prompt = medical_prompt_template(medical_sample)
    # # #创建数据生成器
    # synthetic_data_generator = create_openai_data_generator(
    #     output_schema=MedicalBilling,
    #     llm=ChatOpenAI(model=os.getenv("OPENAI_LLM_MODEL","gpt-4o-mini"),temperature=1),  # You'll need to replace with your actual Language Model instance
    #     prompt=medical_prompt,
    # )

    # # 生成10条合成的医疗账单记录
    # synthetic_results = synthetic_data_generator.generate(
    #     subject="medical_billing",
    #     extra="the name must be chosen at random. Make it something you wouldn't normally choose.",
    #     runs=10,
    # )

    # --------------------------------------

    # 其他实现
    # chain = create_data_generation_chain(model)
    # reponse_json = chain({"fields": ["blue", "yellow"], "preferences": {}})
    # reponse_json = chain(
    #     {
    #         "fields": {"colors": ["blue", "yellow"]},
    #         "preferences": {"style": "Make it in a style of a weather forecast."},
    #     }
    # )
    # reponse_json = chain(
    #     {
    #         "fields": {"actor": "Tom Hanks", "movies": ["Forrest Gump", "Green Mile"]},
    #         "preferences": None,
    #     }
    # )
    # reponse_json = chain(
    #     {
    #         "fields": [
    #             {"actor": "Tom Hanks", "movies": ["Forrest Gump", "Green Mile"]},
    #             {"actor": "Mads Mikkelsen", "movies": ["Hannibal", "Another round"]},
    #         ],
    #         "preferences": {"minimum_length": 200, "style": "gossip"},
    #     }
    # )
    # print(reponse_json)

    # --------------------------------------

    # 生成示例数据集以进行提取基准测试
    dataset = film_sample_data(model)
    # print(dataset)
    # 从生成的示例中提取
    # llm = OpenAI()
    # parser = PydanticOutputParser(pydantic_object=Actor)
    # prompt = PromptTemplate(
    #     template="Extract fields from a given text.\n{format_instructions}\n{text}\n",
    #     input_variables=["text"],
    #     partial_variables={"format_instructions": parser.get_format_instructions()},
    # )
    # _input = prompt.format_prompt(text=dataset[0][0]["text"])
    # output = llm.invoke(_input.to_string())
    # parsed = parser.parse(output)
    # print(parsed)
    # flag = (parsed.Actor == dataset[1][0]["Actor"]) & (parsed.Film == dataset[1][0]["Film"])
    # print(flag)

    # 提取器
    extractor = create_extraction_chain_pydantic(pydantic_schema=Actor, llm=model)
    extracted = extractor.run(dataset[0][1]["text"])
    print(extracted)
    flag = (extracted[0].Actor == dataset[1][1]["Actor"]) & (extracted[0].Film == dataset[1][1]["Film"])
    print(flag)

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))