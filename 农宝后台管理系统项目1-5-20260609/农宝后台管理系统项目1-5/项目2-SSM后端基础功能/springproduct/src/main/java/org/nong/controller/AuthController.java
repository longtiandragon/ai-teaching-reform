package org.nong.controller;

import org.nong.common.Result;
import org.nong.entity.SysUser;
import org.nong.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/yjnb/system")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class AuthController {

    @Autowired
    private ISysUserService userService;

    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");

        if (username == null || username.trim().isEmpty()) {
            return Result.error("Username is required");
        }
        if (password == null || password.trim().isEmpty()) {
            return Result.error("Password is required");
        }

        SysUser user = userService.selectByUsername(username);
        if (user == null || !password.equals(user.getPassword())) {
            return Result.error("Username or password is incorrect");
        }
        if (user.getStatus() != null && user.getStatus() == 1) {
            return Result.error("User account is disabled");
        }

        user.setLoginIp("127.0.0.1");
        user.setLoginDate(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        userService.update(user);

        Map<String, Object> data = new HashMap<>();
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname() != null ? user.getNickname() : user.getUsername());
        data.put("token", "TOKEN_" + user.getUsername() + "_" + UUID.randomUUID().toString().replace("-", ""));
        data.put("role", "admin".equals(user.getUsername()) ? "超级管理员" : "普通用户");
        data.put("userId", user.getId());
        return Result.success("Login successful", data);
    }

    @PostMapping("/logout")
    public Result<Void> logout(@RequestBody(required = false) Map<String, String> logoutRequest) {
        return Result.success("Logout successful");
    }

    @GetMapping("/userInfo")
    public Result<Map<String, Object>> userInfo(@RequestParam(required = false) String token) {
        Map<String, Object> data = new HashMap<>();
        data.put("username", "admin");
        data.put("nickname", "admin");
        data.put("role", "超级管理员");
        return Result.success(data);
    }

    @GetMapping("/test")
    public Result<String> test() {
        return Result.success("SSM auth API is running");
    }
}
