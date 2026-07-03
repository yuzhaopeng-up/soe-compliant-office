---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '189e07fe-3d51-45b0-9e08-9f145fa40cb0'
  PropagateID: '189e07fe-3d51-45b0-9e08-9f145fa40cb0'
  ReservedCode1: '584ca3c4-e649-4b07-b26d-84b329e68aa7'
  ReservedCode2: '584ca3c4-e649-4b07-b26d-84b329e68aa7'
---

# Root-Cause-Mapper Skill 手动上传指南

由于当前环境缺少GitHub CLI和认证token，请按以下步骤手动上传文件到GitHub私有仓库。

## 仓库信息
- **仓库**: yuzhaopeng-up/openclaw-workspace
- **目标路径**: `02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/`
- **提交信息**: `Add Root-Cause-Mapper skill for Level 5 (fault topology analysis)`

## 需要上传的文件

1. **SKILL.md** → `02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/SKILL.md`
2. **references/pipeline-phases.md** → `02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/references/pipeline-phases.md`
3. **references/demo-data.md** → `02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/references/demo-data.md`
4. **references/classroom-script.md** → `02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/references/classroom-script.md`

## 方法1：使用GitHub网站手动上传（推荐）

1. 打开浏览器访问: https://github.com/yuzhaopeng-up/openclaw-workspace
2. 导航到 `02-telecom-ai/2026-07-jiangxi-training/skills/` 目录
3. 点击 "Add file" → "Upload files"
4. 拖拽或选择本地文件:
   - `C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\SKILL.md`
   - `C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\references\pipeline-phases.md`
   - `C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\references\demo-data.md`
   - `C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\references\classroom-script.md`
5. 在路径框中输入: `02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/`
6. 填写提交信息: `Add Root-Cause-Mapper skill for Level 5 (fault topology analysis)`
7. 点击 "Commit changes"

## 方法2：使用GitHub Desktop

1. 下载安装GitHub Desktop: https://desktop.github.com/
2. 登录您的GitHub账号
3. Clone仓库: `yuzhaopeng-up/openclaw-workspace`
4. 在本地创建目录结构:
   ```
   openclaw-workspace/
   └── 02-telecom-ai/
       └── 2026-07-jiangxi-training/
           └── skills/
               └── Root-Cause-Mapper/
                   ├── SKILL.md
                   └── references/
                       ├── pipeline-phases.md
                       ├── demo-data.md
                       └── classroom-script.md
   ```
5. 复制本地文件到对应位置
6. 在GitHub Desktop中提交，填写提交信息
7. 点击 "Push origin"

## 方法3：使用Git命令行（如果已安装Git）

```bash
# 1. 克隆仓库（如果还没有）
git clone https://github.com/yuzhaopeng-up/openclaw-workspace.git
cd openclaw-workspace

# 2. 创建目录结构
mkdir -p 02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/references

# 3. 复制文件
cp "C:/Users/于兆鹏/.config/TeleAgent/skills/Root-Cause-Mapper/SKILL.md" \
   02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/

cp "C:/Users/于兆鹏/.config/TeleAgent/skills/Root-Cause-Mapper/references/pipeline-phases.md" \
   02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/references/

cp "C:/Users/于兆鹏/.config/TeleAgent/skills/Root-Cause-Mapper/references/demo-data.md" \
   02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/references/

cp "C:/Users/于兆鹏/.config/TeleAgent/skills/Root-Cause-Mapper/references/classroom-script.md" \
   02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper/references/

# 4. 提交
git add .
git commit -m "Add Root-Cause-Mapper skill for Level 5 (fault topology analysis)"

# 5. 推送
git push origin main
```

## 方法4：使用GitHub API（需要Token）

如果您有GitHub Personal Access Token，可以使用以下PowerShell脚本：

```powershell
# 设置token（替换为您的实际token）
$env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxx"

# 运行上传脚本
python upload_to_github.py
```

创建token步骤:
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限（访问私有仓库）
4. 生成并复制token

## 文件内容预览

所有4个文件已读取并准备好上传，内容完整。主要文件包括:

- **SKILL.md**: 主技能文件，包含4-Phase编排协议、3层推理规则、降级策略等
- **pipeline-phases.md**: 4个Phase的详细prompt模板和JSON输出契约
- **demo-data.md**: 脱敏演示数据，包含标准用例和4个变体场景
- **classroom-script.md**: 课堂脚本、学员指南和自查清单

## 验证上传

上传完成后，请访问以下URL验证文件是否存在:
https://github.com/yuzhaopeng-up/openclaw-workspace/tree/main/02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper

---

**提示**: 如果环境中有GitHub CLI (gh)，可以运行 `gh auth login` 登录后，使用:
```bash
gh repo clone yuzhaopeng-up/openclaw-workspace
```
然后按方法3操作。

> AI生成