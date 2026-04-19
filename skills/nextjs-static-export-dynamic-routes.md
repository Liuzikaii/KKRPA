# Skill: Next.js Static Export 动态路由修复

## 问题描述

当 Next.js 使用 `output: 'export'`（静态导出）配置时，所有动态路由（如 `[id]`、`[slug]`）必须提供 `generateStaticParams()` 函数来告知构建器需要预渲染哪些页面。

**典型报错：**
```
Error: Page "/workflows/[id]" is missing "generateStaticParams()" so it cannot be used with "output: export" config.
```

## 适用场景

- Electron 桌面应用打包（使用 `next build` + `next export`）
- 任何使用 `output: 'export'` 的 Next.js 项目
- 动态路由的参数来自数据库/API，无法在构建时确定

## 解决方案

将动态路由 `[id]` 替换为静态路由 + 查询参数（Query Params）。

### Step 1: 创建静态路由页面

将 `app/xxx/[id]/page.tsx` 替换为 `app/xxx/editor/page.tsx`（或其他有意义的名称），使用 `useSearchParams()` 读取参数：

```tsx
// ❌ 旧方式 — app/workflows/[id]/page.tsx
import { useParams } from 'next/navigation';
const { id } = useParams<{ id: string }>();

// ✅ 新方式 — app/workflows/editor/page.tsx
import { useSearchParams } from 'next/navigation';
const searchParams = useSearchParams();
const id = searchParams.get('id') || '';
```

### Step 2: 更新所有导航链接

```tsx
// ❌ 旧方式
router.push(`/workflows/${wf.id}`);

// ✅ 新方式
router.push(`/workflows/editor?id=${wf.id}`);
```

### Step 3: 删除旧的动态路由目录

```bash
rm -rf frontend/src/app/workflows/[id]
```

## 注意事项

- 页面必须标记为 `'use client'`，因为 `useSearchParams()` 是客户端 Hook
- 所有引用旧路由的地方（`router.push`、`<Link>`、`<a>`）都需要更新
- 如果有多个动态路由（如 `[id]`、`[slug]`），每个都需要同样处理

## 本项目已应用的修改

| 文件 | 操作 |
|------|------|
| `frontend/src/app/workflows/editor/page.tsx` | 新建 — 替代 `[id]` 路由 |
| `frontend/src/app/workflows/[id]/page.tsx` | 删除 |
| `frontend/src/app/workflows/page.tsx` | 修改 — 更新两处 `router.push()` |
| `frontend/next.config.ts` | 无需修改 — 保持 `output: 'export'` |

## 相关配置

```ts
// frontend/next.config.ts
const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
};
```
