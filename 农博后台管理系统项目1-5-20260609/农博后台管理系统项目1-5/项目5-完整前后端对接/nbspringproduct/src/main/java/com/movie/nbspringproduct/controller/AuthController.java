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

/**
 * 认证控制器 - 登录/登出
 */
@RestController
@RequestMapping("/dev-api/yjnb/system")
@CrossOrigin
public class AuthController {
    
    @Autowired
    private ISysUserService userService;
    
    /**
     * 用户登录接口
     * 
     * 前端调用: POST /dev-api/yjnb/system/login
     * 请求体: { "username": "admin", "password": "123456" }
     * 
     * @param loginRequest 登录请求参数
     * @return 登录结果（包含 token 和用户信息）
     */
    @PostMapping("/login")
    public Result<Map<String, Object>> login(@RequestBody Map<String, String> loginRequest) {
        String username = loginRequest.get("username");
        String password = loginRequest.get("password");
        
        // 参数校验
        if (username == null || username.trim().isEmpty()) {
            return Result.error("用户名不能为空");
        }
        if (password == null || password.trim().isEmpty()) {
            return Result.error("密码不能为空");
        }
        
        try {
            // 1. 查询用户
            LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(SysUser::getUsername, username);
            wrapper.eq(SysUser::getDelFlag, 0); // 未删除
            SysUser user = userService.getOne(wrapper);
            
            // 2. 验证用户是否存在
            if (user == null) {
                return Result.error("用户名或密码错误");
            }
            
            // 3. 验证用户状态
            if (user.getStatus() != null && user.getStatus() == 1) {
                return Result.error("该账号已被停用，请联系管理员");
            }
            
            // 4. 验证密码（简单比对，实际项目应该使用加密）
            if (!password.equals(user.getPassword())) {
                return Result.error("用户名或密码错误");
            }
            
            // 5. 生成 Token（简化版，实际项目应使用 JWT）
            String token = generateToken(user);
            
            // 6. 更新登录信息
            user.setLoginIp(getRequestIp());
            user.setLoginDate(getCurrentDateTime());
            userService.updateById(user);
            
            // 7. 构造返回数据
            Map<String, Object> data = new HashMap<>();
            data.put("username", user.getUsername());
            data.put("nickname", user.getNickname() != null ? user.getNickname() : user.getUsername());
            data.put("token", token);
            data.put("role", getRoleName(user));
            data.put("userId", user.getId());
            
            System.out.println("✅ 用户登录成功: " + username);
            return Result.success("登录成功", data);
            
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("登录失败：" + e.getMessage());
        }
    }
    
    /**
     * 用户登出接口
     * 
     * 前端调用: POST /dev-api/yjnb/system/logout
     * 请求体: { "token": "xxx" }
     * 
     * @param logoutRequest 登出请求参数
     * @return 登出结果
     */
    @PostMapping("/logout")
    public Result<Void> logout(@RequestBody Map<String, String> logoutRequest) {
        String token = logoutRequest.get("token");
        
        // 实际项目中应该将 token 加入黑名单或从 Redis 中删除
        System.out.println("✅ 用户登出成功, token: " + token);
        
        return Result.success("登出成功");
    }
    
    /**
     * 获取当前登录用户信息
     * 
     * 前端调用: GET /dev-api/yjnb/system/userInfo
     * 
     * @param token 用户 token
     * @return 用户信息
     */
    @GetMapping("/userInfo")
    public Result<Map<String, Object>> getUserInfo(@RequestParam(required = false) String token) {
        // 简化版：从 token 中解析用户名（实际项目应该从 JWT 中解析）
        if (token == null || token.isEmpty()) {
            return Result.error("未登录");
        }
        
        try {
            String username = parseTokenToUsername(token);
            
            LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(SysUser::getUsername, username);
            wrapper.eq(SysUser::getDelFlag, 0);
            SysUser user = userService.getOne(wrapper);
            
            if (user == null) {
                return Result.error("用户不存在");
            }
            
            Map<String, Object> data = new HashMap<>();
            data.put("username", user.getUsername());
            data.put("nickname", user.getNickname());
            data.put("role", getRoleName(user));
            data.put("userId", user.getId());
            
            return Result.success(data);
            
        } catch (Exception e) {
            return Result.error("获取用户信息失败");
        }
    }
    
    /**
     * 测试接口
     */
    @GetMapping("/test")
    public Result<String> test() {
        return Result.success("认证接口正常运行");
    }
    
    // ==================== 私有方法 ====================
    
    /**
     * 生成 Token（简化版）
     * 实际项目应使用 JWT
     */
    private String generateToken(SysUser user) {
        // 简单生成：USER_用户名_UUID
        // 实际项目中应该使用 JWT 生成带过期时间的 token
        return "TOKEN_" + user.getUsername() + "_" + UUID.randomUUID().toString().replace("-", "");
    }
    
    /**
     * 从 Token 中解析用户名（简化版）
     */
    private String parseTokenToUsername(String token) {
        // 简化版：从 TOKEN_username_uuid 中提取 username
        if (token.startsWith("TOKEN_")) {
            String[] parts = token.split("_");
            if (parts.length >= 2) {
                return parts[1];
            }
        }
        return null;
    }
    
    /**
     * 获取角色名称
     */
    private String getRoleName(SysUser user) {
        // 简化处理：根据用户名判断角色
        // 实际项目应该从用户角色关联表中查询
        if ("admin".equals(user.getUsername())) {
            return "超级管理员";
        } else {
            return "普通用户";
        }
    }
    
    /**
     * 获取当前时间
     */
    private String getCurrentDateTime() {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        return LocalDateTime.now().format(formatter);
    }
    
    /**
     * 获取请求 IP（简化版）
     */
    private String getRequestIp() {
        // 实际项目中应该从 HttpServletRequest 中获取真实 IP
        return "127.0.0.1";
    }
}









