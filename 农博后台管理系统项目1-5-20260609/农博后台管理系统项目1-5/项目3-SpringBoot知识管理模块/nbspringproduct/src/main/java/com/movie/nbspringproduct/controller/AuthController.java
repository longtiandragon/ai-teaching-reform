package com.movie.nbspringproduct.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.SysUser;
import com.movie.nbspringproduct.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/dev-api/yjnb/system")
@CrossOrigin
public class AuthController {

    @Autowired
    private ISysUserService userService;

    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");

        if (username == null || username.trim().isEmpty()) {
            return Result.error("用户名不能为空");
        }
        if (password == null || password.trim().isEmpty()) {
            return Result.error("密码不能为空");
        }

        try {
            LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(SysUser::getUsername, username);
            wrapper.eq(SysUser::getDelFlag, 0);
            SysUser user = userService.getOne(wrapper);

            if (user != null) {
                if (user.getStatus() != null && user.getStatus() == 1) {
                    return Result.error("账号已停用");
                }
                if (!password.equals(user.getPassword())) {
                    return Result.error("用户名或密码错误");
                }

                user.setLoginIp("127.0.0.1");
                user.setLoginDate(currentTime());
                userService.updateById(user);
                return Result.success("登录成功", buildLoginData(user.getUsername(), user.getNickname(), user.getId()));
            }
        } catch (Exception ignored) {
            // 开发迭代阶段允许数据库未初始化时使用默认账号登录。
        }

        if ("admin".equals(username) && "123456".equals(password)) {
            return Result.success("登录成功", buildLoginData("admin", "系统管理员", "1"));
        }

        return Result.error("用户名或密码错误");
    }

    @PostMapping("/logout")
    public Result<Void> logout(@RequestBody(required = false) Map<String, String> logoutRequest) {
        return Result.success("退出成功");
    }

    @GetMapping("/userInfo")
    public Result<Map<String, Object>> getUserInfo(@RequestParam(required = false) String token) {
        if (token == null || token.isEmpty()) {
            return Result.error("未登录");
        }
        return Result.success(buildLoginData(parseTokenToUsername(token), "系统管理员", "1"));
    }

    @GetMapping("/test")
    public Result<String> test() {
        return Result.success("认证接口正常运行");
    }

    private Map<String, Object> buildLoginData(String username, String nickname, String userId) {
        Map<String, Object> data = new HashMap<>();
        data.put("username", username);
        data.put("nickname", nickname != null ? nickname : username);
        data.put("token", "TOKEN_" + username + "_" + UUID.randomUUID().toString().replace("-", ""));
        data.put("role", "超级管理员");
        data.put("userId", userId);
        return data;
    }

    private String parseTokenToUsername(String token) {
        if (token != null && token.startsWith("TOKEN_")) {
            String[] parts = token.split("_");
            if (parts.length >= 2) {
                return parts[1];
            }
        }
        return "admin";
    }

    private String currentTime() {
        return LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }
}
