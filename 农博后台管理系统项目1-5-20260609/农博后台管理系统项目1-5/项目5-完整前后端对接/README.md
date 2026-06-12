# 项目5：完整前后端对接

本阶段是最终完整版本，包含完整 Spring Boot 后端和 Vue 前端。

## 后端

目录：`nbspringproduct`

包含模块：

- 登录认证
- 系统管理
- 数据统计
- 文件上传
- 专家管理
- 图文课程管理
- 视频课程管理
- 补贴政策管理
- 信贷信息管理
- 农事服务管理
- 农产品管理
- 市场行情管理
- 广告管理

启动：

```bash
cd nbspringproduct
mvn spring-boot:run
```

默认端口：`8081`。

## 前端

目录：`nbvueproject`

前端没有复制 `node_modules` 和 `dist`，启动前需要安装依赖：

```bash
cd nbvueproject
npm install
npm run dev
```

## 对接说明

- 前端通过 Axios 请求后端接口。
- 后端接口前缀主要为 `/dev-api/yjnb/...`。
- 登录、系统管理和业务管理页面都在本阶段完成前后端对接。

