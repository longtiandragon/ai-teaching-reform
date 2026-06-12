package org.nong.controller;

import org.nong.common.PageQuery;
import org.nong.common.Result;
import org.nong.entity.SysConfig;
import org.nong.entity.SysRole;
import org.nong.entity.SysUser;
import org.nong.service.ISysConfigService;
import org.nong.service.ISysRoleService;
import org.nong.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/system")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class SystemManagementController {

    @Autowired
    private ISysUserService userService;

    @Autowired
    private ISysRoleService roleService;

    @Autowired
    private ISysConfigService configService;

    @GetMapping("/test")
    public Result<String> test() {
        return Result.success("SSM system API is running");
    }

    @GetMapping("/user/list")
    public Result<SysUser> getUserList(PageQuery pageQuery,
                                       @RequestParam(required = false) String username,
                                       @RequestParam(required = false) String nickname,
                                       @RequestParam(required = false) String phonenumber,
                                       @RequestParam(required = false) Integer status) {
        Map<String, Object> params = new HashMap<>();
        params.put("offset", pageQuery.getOffset());
        params.put("pageSize", pageQuery.getPageSize());
        params.put("username", username);
        params.put("nickname", nickname);
        params.put("phonenumber", phonenumber);
        params.put("status", status);
        return userService.selectList(params);
    }

    @GetMapping("/user/{id}")
    public Result<SysUser> getUserById(@PathVariable String id) {
        SysUser user = userService.selectById(id);
        if (user != null) {
            user.setPassword(null);
        }
        return Result.success(user);
    }

    @PostMapping("/user")
    public Result<String> addUser(@RequestBody SysUser user) {
        if (user.getUsername() == null || user.getUsername().isEmpty()) {
            return Result.error("Username is required");
        }
        if (userService.selectByUsername(user.getUsername()) != null) {
            return Result.error("Username already exists");
        }
        if (user.getStatus() == null) {
            user.setStatus(0);
        }
        if (user.getDelFlag() == null) {
            user.setDelFlag(0);
        }
        if (user.getPassword() == null || user.getPassword().isEmpty()) {
            user.setPassword("123456");
        }
        userService.insert(user);
        return Result.success("Added successfully");
    }

    @PutMapping("/user")
    public Result<String> updateUser(@RequestBody SysUser user) {
        if (user.getId() == null || user.getId().isEmpty()) {
            return Result.error("User id is required");
        }
        if (user.getPassword() != null && user.getPassword().isEmpty()) {
            user.setPassword(null);
        }
        userService.update(user);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/user/{id}")
    public Result<String> deleteUser(@PathVariable String id) {
        userService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @PutMapping("/user/resetPassword/{id}")
    public Result<String> resetPassword(@PathVariable String id) {
        userService.resetPassword(id, "123456");
        return Result.success("Password reset to 123456");
    }

    @GetMapping("/role/list")
    public Result<SysRole> getRoleList(PageQuery pageQuery,
                                       @RequestParam(required = false) String roleName,
                                       @RequestParam(required = false) String roleKey,
                                       @RequestParam(required = false) Integer status) {
        Map<String, Object> params = new HashMap<>();
        params.put("offset", pageQuery.getOffset());
        params.put("pageSize", pageQuery.getPageSize());
        params.put("roleName", roleName);
        params.put("roleKey", roleKey);
        params.put("status", status);
        return roleService.selectList(params);
    }

    @GetMapping("/role/all")
    public Result<SysRole> getAllRoles() {
        Map<String, Object> params = new HashMap<>();
        params.put("status", 0);
        return roleService.selectList(params);
    }

    @GetMapping("/role/{id}")
    public Result<SysRole> getRoleById(@PathVariable String id) {
        return Result.success(roleService.selectById(id));
    }

    @PostMapping("/role")
    public Result<String> addRole(@RequestBody SysRole role) {
        if (role.getRoleName() == null || role.getRoleName().isEmpty()) {
            return Result.error("Role name is required");
        }
        if (role.getRoleKey() == null || role.getRoleKey().isEmpty()) {
            return Result.error("Role key is required");
        }
        if (role.getStatus() == null) {
            role.setStatus(0);
        }
        if (role.getRoleSort() == null) {
            role.setRoleSort(0);
        }
        if (role.getDelFlag() == null) {
            role.setDelFlag(0);
        }
        roleService.insert(role);
        return Result.success("Added successfully");
    }

    @PutMapping("/role")
    public Result<String> updateRole(@RequestBody SysRole role) {
        if (role.getId() == null || role.getId().isEmpty()) {
            return Result.error("Role id is required");
        }
        roleService.update(role);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/role/{id}")
    public Result<String> deleteRole(@PathVariable String id) {
        roleService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @GetMapping("/config/all")
    public Result<Map<String, String>> getAllConfigs() {
        List<SysConfig> configs = configService.selectAll();
        Map<String, String> configMap = new HashMap<>();
        for (SysConfig config : configs) {
            configMap.put(config.getConfigKey(), config.getConfigValue());
        }
        return Result.success(configMap);
    }

    @GetMapping({"/config/{key}", "/config/key/{key}"})
    public Result<String> getConfigByKey(@PathVariable String key) {
        SysConfig config = configService.selectByKey(key);
        return Result.success(config == null ? null : config.getConfigValue());
    }

    @PostMapping("/config/batch")
    public Result<String> batchUpdateConfig(@RequestBody Map<String, String> configMap) {
        for (Map.Entry<String, String> entry : configMap.entrySet()) {
            saveConfigValue(entry.getKey(), entry.getValue());
        }
        return Result.success("Saved successfully");
    }

    @PostMapping("/config")
    public Result<String> saveConfig(@RequestBody SysConfig config) {
        if (config.getConfigKey() == null || config.getConfigKey().isEmpty()) {
            return Result.error("Config key is required");
        }
        saveConfigValue(config.getConfigKey(), config.getConfigValue());
        return Result.success("Saved successfully");
    }

    private void saveConfigValue(String key, String value) {
        SysConfig config = configService.selectByKey(key);
        if (config == null) {
            config = new SysConfig();
            config.setConfigKey(key);
            config.setConfigName(key);
            config.setConfigValue(value);
            config.setConfigType("N");
            configService.insert(config);
        } else {
            config.setConfigValue(value);
            configService.updateByKey(config);
        }
    }
}
