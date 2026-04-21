# 前端部署指南

本项目使用 Agno 的 AG-UI 协议提供图形化界面，配合 Dojo 前端工具使用。

## 方案一：使用 Dojo 前端（推荐）

### 前置要求
- 已安装 Node.js (推荐 v18 或更高版本)
- 已安装 pnpm (npm install -g pnpm)

### 步骤

1. **克隆 AG-UI 仓库**
   ```bash
   git clone https://github.com/ag-ui-protocol/ag-ui.git
   cd ag-ui
   ```

2. **安装 TypeScript SDK 依赖**
   ```bash
   cd typescript-sdk
   pnpm install
   ```

3. **构建 Agno 集成包**
   ```bash
   cd ../integrations/agno
   pnpm run build
   ```

4. **查看并启动 Dojo 前端**
   参考 ag-ui 仓库中的 Dojo 启动说明，通常是：
   ```bash
   cd dojo  # 或相应的前端目录
   pnpm install
   pnpm dev
   ```

5. **访问界面**
   打开浏览器访问 http://localhost:3000

### 配置 Dojo 与后端连接
确保在 Dojo 中正确配置后端地址为：
- 默认地址: `http://localhost:7777`
- 如在其他机器上运行，替换为相应的 IP 地址

## 方案二：使用 React 组件库

如果你想自定义构建前端界面，可以使用 `@rodrigocoliveira/agno-react` 库：

### 安装
```bash
npm install @rodrigocoliveira/agno-react
```

### 快速使用示例

```jsx
import { AgnoProvider, AgnoChat } from '@rodrigocoliveira/agno-react';
import '@rodrigocoliveira/agno-react/ui';

function App() {
  return (
    <AgnoProvider
      config={{
        endpoint: 'http://localhost:7777',
        mode: 'agent',
        agentId: 'LLM Wiki Assistant',
        userId: 'user-1',
      }}
    >
      <div className="h-screen">
        <AgnoChat>
          <AgnoChat.Messages />
          <AgnoChat.ToolStatus />
          <AgnoChat.Input placeholder="提问关于知识库的问题..." />
        </AgnoChat>
      </div>
    </AgnoProvider>
  );
}

export default App;
```

## 启动后端服务

无论使用哪种前端方案，都需要先启动后端服务：

```bash
python src/app.py
```

后端服务默认运行在 `http://0.0.0.0:7777`
