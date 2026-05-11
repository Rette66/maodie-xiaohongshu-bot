"""
初始化图片数据库
把 images/ 目录下的所有图片加入数据库并打标签
"""
import json
from pathlib import Path
from image_database import ImageDatabase, ImageEntry

def main():
    db = ImageDatabase()
    
    # 原有的3张猫图
    existing_images = [
        {
            "path": "images/maodie/cat1.jpg",
            "prompt": "AI生成艺术化写实人像橘色虎斑英短猫",
            "source": "ai_generated",
            "tags": {
                "expression": "deadpan",
                "head_shape": "extra_round",
                "eye_color": "amber",
                "pose": "front_face",
                "mood": "serious",
                "lighting": "natural",
                "background": "solid_color",
                "usage": ["daily_post", "reaction"],
                "distinctiveness": "medium",
            }
        },
        {
            "path": "images/maodie/cat2.jpg",
            "prompt": "橘色虎斑英短猫，略带生气不屑的傲娇表情",
            "source": "ai_generated",
            "tags": {
                "expression": "disdainful",
                "head_shape": "extra_round",
                "eye_color": "amber",
                "pose": "front_face",
                "mood": "serious",
                "lighting": "natural",
                "background": "solid_color",
                "usage": ["daily_post", "meme"],
                "distinctiveness": "medium",
            }
        },
        {
            "path": "images/maodie/cat3.jpg",
            "prompt": "橘色虎斑英短猫，超大圆形眼睛，呆萌可爱",
            "source": "ai_generated",
            "tags": {
                "expression": "cute",
                "head_shape": "extra_round",
                "eye_color": "amber",
                "pose": "front_face",
                "mood": "cute",
                "lighting": "natural",
                "background": "white",
                "usage": ["daily_post", "cute"],
                "distinctiveness": "medium",
            }
        },
    ]
    
    # 新生成的4张图（根据prompt描述）
    new_images = [
        {
            "path": "images/maodie-generated/image-1---8bab90d6-14bd-4c82-be12-3e243ff78736.png",
            "prompt": "圆头橘色英短猫，死鱼眼正面无表情，直视镜头",
            "source": "ai_generated",
            "tags": {
                "expression": "deadpan",
                "head_shape": "extra_round",
                "eye_color": "amber",
                "pose": "front_face",
                "mood": "serious",
                "lighting": "natural",
                "background": "white",
                "usage": ["daily_post", "reaction", "meme"],
                "distinctiveness": "high",
            }
        },
        {
            "path": "images/maodie-generated/image-2---a8f0f31f-94a4-40a8-85fe-00b34d753ce3.png",
            "prompt": "圆头橘色英短猫，正面肖像",
            "source": "ai_generated",
            "tags": {
                "expression": "deadpan",
                "head_shape": "extra_round",
                "eye_color": "amber",
                "pose": "front_face",
                "mood": "calm",
                "lighting": "natural",
                "background": "white",
                "usage": ["daily_post", "reaction"],
                "distinctiveness": "high",
            }
        },
        {
            "path": "images/maodie-generated/image-3---6a25eb41-2b41-4901-acc5-2ef2adfd49fe.png",
            "prompt": "圆头橘色英短猫正面照",
            "source": "ai_generated",
            "tags": {
                "expression": "deadpan",
                "head_shape": "extra_round",
                "eye_color": "amber",
                "pose": "front_face",
                "mood": "calm",
                "lighting": "natural",
                "background": "white",
                "usage": ["daily_post"],
                "distinctiveness": "high",
            }
        },
        {
            "path": "images/maodie-generated/image-4---72f9c8a3-6af2-4e4d-9761-cbf25234762a.png",
            "prompt": "圆头橘色英短猫正面肖像",
            "source": "ai_generated",
            "tags": {
                "expression": "deadpan",
                "head_shape": "extra_round",
                "eye_color": "amber",
                "pose": "front_face",
                "mood": "calm",
                "lighting": "natural",
                "background": "white",
                "usage": ["daily_post", "reaction"],
                "distinctiveness": "high",
            }
        },
    ]
    
    all_images = existing_images + new_images
    
    added = 0
    for img in all_images:
        img_path = Path(img["path"])
        if not img_path.exists():
            print(f"⚠️ 跳过不存在的图片: {img['path']}")
            continue
        
        try:
            img_id = db.add_image(
                filepath=str(img_path),
                generation_prompt=img["prompt"],
                source=img["source"],
                tags=img["tags"],
            )
            print(f"✅ 添加: {img['path']} -> ID: {img_id}")
            added += 1
        except Exception as e:
            print(f"❌ 添加失败 {img['path']}: {e}")
    
    print(f"\n📊 数据库统计:")
    stats = db.stats()
    print(f"   总图片数: {stats['total_images']}")
    print(f"   按表情: {stats['by_expression']}")
    print(f"   按情绪: {stats['by_mood']}")
    print(f"   按辨识度: {stats['by_distinctiveness']}")
    
    # 导出数据库内容
    print(f"\n📁 数据库路径: {db.db_path}")


if __name__ == "__main__":
    main()
