import re

with open('backend/ai_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_code = """
        import os
        prompt_file_path = os.path.join(os.path.dirname(__file__), "prompts", "deep_research_prompt.md")
        try:
            with open(prompt_file_path, "r", encoding="utf-8") as pf:
                prompt = pf.read()
        except FileNotFoundError:
            raise Exception("프롬프트 파일을 찾을 수 없습니다: " + prompt_file_path)

        prompt = prompt.replace("{gongmae_instructions}", gongmae_instructions)
        prompt = prompt.replace("{current_year}", str(current_year))
        prompt = prompt.replace("{case_number}", str(case_number))
        prompt = prompt.replace("{address}", str(address))
        prompt = prompt.replace("{property_type}", str(property_type))
        prompt = prompt.replace("{appraised_value}", str(appraised_value))
        prompt = prompt.replace("{minimum_value}", str(minimum_value))
        prompt = prompt.replace("{auction_date}", str(auction_date))
        prompt = prompt.replace("{approval_date}", str(approval_date))
        prompt = prompt.replace("{land_area}", str(land_area))
        prompt = prompt.replace("{building_area}", str(building_area))
        prompt = prompt.replace("{risks}", str(risks))
        prompt = prompt.replace("{precautions}", str(precautions))
        prompt = prompt.replace("{tenant_warning}", str(tenant_warning))
        prompt = prompt.replace("{suspended_warning}", str(suspended_warning))
        prompt = prompt.replace("{ended_warning}", str(ended_warning))
        prompt = prompt.replace("{regulated_str}", str(regulated_str))
        prompt = prompt.replace("{house_count}", str(house_count))
        prompt = prompt.replace("{investor_type}", str(investor_type))
        prompt = prompt.replace("{investment_duration}", str(investment_duration))
        prompt = prompt.replace("{target_return}", str(target_return))
        prompt = prompt.replace("{status}", str(status))
        prompt = prompt.replace("{is_ended}", str(is_ended))
        prompt = prompt.replace("{final_date}", str(final_date))
        prompt = prompt.replace("{final_result}", str(final_result))
        prompt = prompt.replace("{history_str}", str(history_str))
        prompt = prompt.replace("{tenants_str}", str(tenants_str))
        prompt = prompt.replace("{pdf_context}", str(pdf_context))
"""

content = re.sub(r'prompt = f\"\"\"(.*?)\"\"\"', new_code.strip(), content, flags=re.DOTALL)

with open('backend/ai_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated ai_analyzer.py")
