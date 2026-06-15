# 项目4：Spring Boot 进阶业务模块

本阶段是在项目3基础上继续迭代的可运行版本，包含 Spring Boot 后端和 Vue 前端。登录后可使用知识管理和进阶业务模块。

## 项目3已有功能

- 登录认证
- 系统管理基础入口
- 专家管理
- 图文课程管理
- 视频课程管理
- 文件上传

## 项目4新增功能

- 补贴政策管理
- 信贷信息管理
- 农事服务管理

## 后端

目录：`nbspringproduct`

当前主要 Controller：

```text
AuthController.java
SystemManagementController.java
FileUploadController.java
NbExpertController.java
NbGraphicCourseController.java
NbVideoCourseController.java
NbAllowancePolicyController.java
NbCreditLoanController.java
NbServiceController.java
```

启动后端：

```bash
cd nbspringproduct
mvn spring-boot:run
```

默认端口：`8082`

## 前端

目录：`nbvueproject`

项目四前端菜单保留：

- 系统管理
- 知识管理
- 补贴政策
- 信贷管理
- 农事服务

启动前端：

```bash
cd nbvueproject
npm install
npm run dev
```

## 登录账号

```text
admin / 123456
```

说明：如果数据库中已有用户，会优先按数据库用户验证；如果数据库未初始化，也可以用上面的默认账号登录进入页面。

