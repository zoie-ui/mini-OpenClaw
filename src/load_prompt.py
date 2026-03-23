import re
from pathlib import Path
import yaml


def extract_skill_metadata(skill_md_content: str, skill_file_path: str = None) -> dict:
    """
    从标准 SKILL.md 文件中提取 name、description 和 location
    支持 YAML frontmatter 格式
    
    Args:
        skill_md_content: SKILL.md 文件内容
        skill_file_path: SKILL.md 文件路径
        
    Returns:
        包含 name、description 和 location 的字典
    """
    metadata = {"name": None, "description": None, "location": skill_file_path}
    
    # 尝试从 YAML frontmatter 中提取（标准格式）
    # 格式: ---\nkey: value\n---
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', skill_md_content, re.DOTALL)
    
    if frontmatter_match:
        frontmatter_content = frontmatter_match.group(1)
        try:
            # 解析 YAML frontmatter
            frontmatter_data = yaml.safe_load(frontmatter_content)
            if isinstance(frontmatter_data, dict):
                # 提取 name
                if 'name' in frontmatter_data:
                    metadata["name"] = frontmatter_data['name']
                
                # 提取 description
                if 'description' in frontmatter_data:
                    desc = frontmatter_data['description']
                    # 移除引号（如果有）
                    if isinstance(desc, str):
                        desc = desc.strip('"\'')
                        # 截取前 150 字符
                        metadata["description"] = desc[:150]
                
                # 提取 path/location
                if 'path' in frontmatter_data:
                    metadata["location"] = frontmatter_data['path']
        except yaml.YAMLError:
            pass
    
    # 如果 frontmatter 提取失败，降级处理
    if not metadata["name"] or not metadata["description"]:
        lines = skill_md_content.split('\n')
        
        # 从 markdown 标题中提取 name（# Skill Title）
        for line in lines:
            if line.startswith('#') and not line.startswith('##'):
                # 提取标题中的文本
                title = line.lstrip('#').strip()
                if title and not metadata["name"]:
                    # 从 "Weather Skill" 提取 "weather"
                    name_from_title = title.split()[0].lower()
                    metadata["name"] = name_from_title
                break
        
        # 从内容中提取 description
        if not metadata["description"]:
            for line in lines:
                line = line.strip()
                # 跳过空行、标题和代码块
                if line and not line.startswith('#') and not line.startswith('-') and not line.startswith('```'):
                    metadata["description"] = line[:150]
                    break
    
    return metadata


def load_all_skills(skills_dir: str = "skills") -> str:
    """
    动态加载 skills 目录下所有 SKILL.md 文件，提取元数据并格式化为 XML
    
    Args:
        skills_dir: skills 目录路径
        
    Returns:
        格式化后的 XML 字符串
    """
    skills_path = Path(skills_dir)
    available_skills_xml = []
    
    if not skills_path.exists():
        return ""
    
    # 遍历 skills 目录下所有子目录
    for skill_folder in sorted(skills_path.iterdir()):
        if not skill_folder.is_dir():
            continue
            
        skill_file = skill_folder / "SKILL.md"
        if not skill_file.exists():
            continue
        
        try:
            # 读取 SKILL.md 文件
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取元数据（传入文件路径用于 location）
            metadata = extract_skill_metadata(content, str(skill_file))
            
            # 确保必要字段存在（从文件夹名称作为备选）
            if not metadata["name"]:
                metadata["name"] = skill_folder.name
            
            if not metadata["description"]:
                metadata["description"] = f"{metadata['name']} skill"
            
            if not metadata["location"]:
                metadata["location"] = str(skill_file)
            
            # 格式化为 HTML 标签样式
            skill_html = f"""<skill>
  <name>{metadata['name']}</name>
  <description>{metadata['description']}</description>
  <location>{metadata['location']}</location>
</skill>"""
            available_skills_xml.append(skill_html)
            print(f"[✓] 加载 skill: {metadata['name']} from {metadata['location']}")
        except Exception as e:
            print(f"[✗] 加载 skill {skill_folder.name} 失败: {str(e)}")
    
    return "\n".join(available_skills_xml)


def load_markdown_file(file_path: str) -> str:
    """
    加载 markdown 文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容，如果文件不存在返回空字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"[⚠] 文件不存在: {file_path}")
        return ""
    except Exception as e:
        print(f"[⚠] 读取文件失败 {file_path}: {str(e)}")
        return ""


def build_system_prompt(read_tool_name: str = "read_file") -> str:
    """
    构建完整的系统提示词：SYSTEM.md + User.md + base_prompt + skills 信息
    
    Args:
        base_prompt: 基础系统提示词
        read_tool_name: 读取工具的名称
        
    Returns:
        完整的系统提示词
    """
    # 加载 SYSTEM.md
    soul_content = load_markdown_file("SOUL.md")
    
    # 加载 User.md
    user_content = load_markdown_file("USER.md")

    # 加载系统提示词
    system_content = load_markdown_file("SYSTEM.md")
    
    # 加载所有 skills
    available_skills = load_all_skills("skills")
    
    # 构建 skills 部分
    skills_section = f"""
## Skills (mandatory)

Before replying: scan <available_skills> <description> entries.

- If exactly one skill clearly applies: read its SKILL.md at <location> with `{read_tool_name}`, then follow it.
- If multiple could apply: choose the most specific one, then read/follow it.
- If none clearly apply: do not read any SKILL.md.

Constraints: never read more than one skill up front; only read after selecting.
- When a skill drives external API writes, assume rate limits: prefer fewer larger writes, avoid tight one-item loops, serialize bursts when possible, and respect 429/Retry-After.

<available_skills>
{available_skills}
</available_skills>
"""
    
    # 按顺序拼接所有部分
    full_prompt_parts = []
    
    if soul_content:
        full_prompt_parts.append(soul_content)
    
    if user_content:
        full_prompt_parts.append(user_content)
    
    full_prompt_parts.append(system_content)
    full_prompt_parts.append(skills_section)
    
    return "\n\n".join(full_prompt_parts)
