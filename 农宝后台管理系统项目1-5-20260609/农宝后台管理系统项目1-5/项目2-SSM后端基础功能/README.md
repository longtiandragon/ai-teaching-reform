# 项目2：SSM 后端基础功能

本阶段放的是 SSM 后端源码，来源于工作区 `springproduct`。

## 项目内容

```text
springproduct
├── pom.xml
└── src
    ├── main
    │   ├── java/org/nong
    │   ├── resources
    │   └── webapp
    └── test
```

## 实现范围

- Spring MVC 接口层。
- MyBatis Mapper 和 XML。
- 用户、角色、配置等系统基础功能。
- 专家、课程、补贴、信贷、农事服务等基础 CRUD。
- 文件上传、跨域、统一返回结果。

## 启动方式

1. 修改 `springproduct/src/main/resources/jdbc.properties` 中的数据库配置。
2. 准备 MySQL 数据库。
3. 使用 Maven 打包：

```bash
mvn clean package
```

4. 将生成的 WAR 部署到 Tomcat。

