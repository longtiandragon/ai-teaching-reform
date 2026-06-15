package com.movie.nbspringproduct.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.movie.nbspringproduct.common.PageQuery;
import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.SysConfig;
import com.movie.nbspringproduct.entity.SysRole;
import com.movie.nbspringproduct.entity.SysUser;
import com.movie.nbspringproduct.service.ISysConfigService;
import com.movie.nbspringproduct.service.ISysRoleService;
import com.movie.nbspringproduct.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 系统管理Controller
 */
@RestController
@RequestMapping("/api/system")
@CrossOrigin
public class SystemManagementController {
    
    @Autowired
    private ISysUserService userService;
    
    @Autowired
    private ISysRoleService roleService;
    
    @Autowired
    private ISysConfigService configService;
    
    // ==================== 测试接口 ====================
    
    /**
     * 测试接口
     */
    @GetMapping("/test")
    public Result<String> test() {
        return Result.success("系统管理接口正常");
    }
    
    // ==================== 用户管理 ====================
    
    /**
     * 分页查询用户列表
     */
    @GetMapping("/user/list")
    public Result<IPage<SysUser>> getUserList(PageQuery pageQuery,
                                               @RequestParam(required = false) String username,
                                               @RequestParam(required = false) Integer status) {
        Page<SysUser> page = new Page<>(pageQuery.getPageNum(), pageQuery.getPageSize());
        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
        
        // 查询条件
        if (username != null && !username.isEmpty()) {
            wrapper.like(SysUser::getUsername, username)
                   .or()
                   .like(SysUser::getNickname, username);
        }
        if (status != null) {
            wrapper.eq(SysUser::getStatus, status);
        }
        
        // 未删除的用户
        wrapper.eq(SysUser::getDelFlag, 0);
        wrapper.orderByDesc(SysUser::getCreateTime);
        
        IPage<SysUser> result = userService.page(page, wrapper);
        
        // 清除密码信息
        result.getRecords().forEach(user -> user.setPassword(null));
        
        return Result.success(result);
    }
    
    /**
     * 获取用户详情
     */
    @GetMapping("/user/{id}")
    public Result<SysUser> getUserById(@PathVariable String id) {
        SysUser user = userService.getById(id);
        if (user != null) {
            user.setPassword(null);
        }
        return Result.success(user);
    }
    
    /**
     * 新增用户
     */
    @PostMapping("/user")
    public Result<String> addUser(@RequestBody SysUser user) {
        if (user.getUsername() == null || user.getUsername().isEmpty()) {
            return Result.error("用户名不能为空");
        }
        
        // 检查用户名是否已存在
        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysUser::getUsername, user.getUsername());
        long count = userService.count(wrapper);
        if (count > 0) {
            return Result.error("用户名已存在");
        }
        
        // 设置默认值
        if (user.getStatus() == null) {
            user.setStatus(0);
        }
        user.setDelFlag(0);
        
        // 如果没有设置密码，使用默认密码
        if (user.getPassword() == null || user.getPassword().isEmpty()) {
            user.setPassword("123456");
        }
        
        boolean success = userService.save(user);
        return success ? Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改用户
     */
    @PutMapping("/user")
    public Result<String> updateUser(@RequestBody SysUser user) {
        if (user.getId() == null) {
            return Result.error("用户ID不能为空");
        }
        
        // 不允许修改密码（通过重置密码接口）
        user.setPassword(null);
        
        boolean success = userService.updateById(user);
        return success ? Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除用户（逻辑删除）
     */
    @DeleteMapping("/user/{id}")
    public Result<String> deleteUser(@PathVariable String id) {
        SysUser user = userService.getById(id);
        if (user != null) {
            user.setDelFlag(1);
            boolean success = userService.updateById(user);
            return success ? Result.success("删除成功") : Result.error("删除失败");
        }
        return Result.error("用户不存在");
    }
    
    /**
     * 重置用户密码
     */
    @PutMapping("/user/resetPassword/{id}")
    public Result<String> resetPassword(@PathVariable String id) {
        String newPassword = userService.resetPassword(id);
        return Result.success("密码已重置为：" + newPassword);
    }
    
    // ==================== 角色管理 ====================
    
    /**
     * 分页查询角色列表
     */
    @GetMapping("/role/list")
    public Result<IPage<SysRole>> getRoleList(PageQuery pageQuery,
                                               @RequestParam(required = false) String roleName) {
        Page<SysRole> page = new Page<>(pageQuery.getPageNum(), pageQuery.getPageSize());
        LambdaQueryWrapper<SysRole> wrapper = new LambdaQueryWrapper<>();
        
        // 查询条件
        if (roleName != null && !roleName.isEmpty()) {
            wrapper.like(SysRole::getRoleName, roleName);
        }
        
        // 未删除的角色
        wrapper.eq(SysRole::getDelFlag, 0);
        wrapper.orderByAsc(SysRole::getRoleSort);
        
        IPage<SysRole> result = roleService.page(page, wrapper);
        return Result.success(result);
    }
    
    /**
     * 获取所有角色（不分页）
     */
    @GetMapping("/role/all")
    public Result<List<SysRole>> getAllRoles() {
        LambdaQueryWrapper<SysRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysRole::getDelFlag, 0);
        wrapper.eq(SysRole::getStatus, 0);
        wrapper.orderByAsc(SysRole::getRoleSort);
        List<SysRole> roles = roleService.list(wrapper);
        return Result.success(roles);
    }
    
    /**
     * 获取角色详情
     */
    @GetMapping("/role/{id}")
    public Result<SysRole> getRoleById(@PathVariable String id) {
        SysRole role = roleService.getById(id);
        return Result.success(role);
    }
    
    /**
     * 新增角色
     */
    @PostMapping("/role")
    public Result<String> addRole(@RequestBody SysRole role) {
        if (role.getRoleName() == null || role.getRoleName().isEmpty()) {
            return Result.error("角色名称不能为空");
        }
        if (role.getRoleKey() == null || role.getRoleKey().isEmpty()) {
            return Result.error("权限字符不能为空");
        }
        
        // 检查角色名称是否已存在
        LambdaQueryWrapper<SysRole> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysRole::getRoleName, role.getRoleName());
        long count = roleService.count(wrapper);
        if (count > 0) {
            return Result.error("角色名称已存在");
        }
        
        // 设置默认值
        if (role.getStatus() == null) {
            role.setStatus(0);
        }
        if (role.getRoleSort() == null) {
            role.setRoleSort(0);
        }
        role.setDelFlag(0);
        
        boolean success = roleService.save(role);
        return success ? Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改角色
     */
    @PutMapping("/role")
    public Result<String> updateRole(@RequestBody SysRole role) {
        if (role.getId() == null) {
            return Result.error("角色ID不能为空");
        }
        
        boolean success = roleService.updateById(role);
        return success ? Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除角色（逻辑删除）
     */
    @DeleteMapping("/role/{id}")
    public Result<String> deleteRole(@PathVariable String id) {
        SysRole role = roleService.getById(id);
        if (role != null) {
            role.setDelFlag(1);
            boolean success = roleService.updateById(role);
            return success ? Result.success("删除成功") : Result.error("删除失败");
        }
        return Result.error("角色不存在");
    }
    
    // ==================== 系统配置 ====================
    
    /**
     * 获取所有配置
     */
    @GetMapping("/config/all")
    public Result<Map<String, String>> getAllConfig() {
        Map<String, String> configMap = configService.getAllConfigMap();
        return Result.success(configMap);
    }
    
    /**
     * 根据键名获取配置值
     */
    @GetMapping("/config/{key}")
    public Result<String> getConfigByKey(@PathVariable String key) {
        String value = configService.getConfigValueByKey(key);
        return Result.success(value);
    }
    
    /**
     * 批量保存配置
     */
    @PostMapping("/config/batch")
    public Result<String> saveConfigBatch(@RequestBody Map<String, String> configMap) {
        configService.saveConfigBatch(configMap);
        return Result.success("保存成功");
    }
    
    /**
     * 保存单个配置
     */
    @PostMapping("/config")
    public Result<String> saveConfig(@RequestBody SysConfig config) {
        if (config.getConfigKey() == null || config.getConfigKey().isEmpty()) {
            return Result.error("配置键名不能为空");
        }
        
        LambdaQueryWrapper<SysConfig> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysConfig::getConfigKey, config.getConfigKey());
        SysConfig existConfig = configService.getOne(wrapper);
        
        boolean success;
        if (existConfig != null) {
            // 更新
            existConfig.setConfigValue(config.getConfigValue());
            existConfig.setConfigName(config.getConfigName());
            existConfig.setRemark(config.getRemark());
            success = configService.updateById(existConfig);
        } else {
            // 新增
            if (config.getConfigType() == null) {
                config.setConfigType("N");
            }
            success = configService.save(config);
        }
        
        return success ? Result.success("保存成功") : Result.error("保存失败");
    }
}

