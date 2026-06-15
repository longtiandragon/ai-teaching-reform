package org.nong.controller;

import org.nong.common.PageQuery;
import org.nong.common.Result;
import org.nong.entity.NbExpert;
import org.nong.service.INbExpertService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/yjnb/expert")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbExpertController {
    
    @Autowired
    private INbExpertService expertService;
    
    @GetMapping("/list")
    public Result<NbExpert> list(PageQuery pageQuery,
                                 @RequestParam(required = false) String name,
                                 @RequestParam(required = false) String specialty,
                                 @RequestParam(required = false) String organization,
                                 @RequestParam(required = false) Integer status) {
        try {
            Map<String, Object> params = new HashMap<>();
            params.put("offset", pageQuery.getOffset());
            params.put("pageSize", pageQuery.getPageSize());
            params.put("name", name);
            params.put("specialty", specialty);
            params.put("organization", organization);
            params.put("status", status);
            return expertService.selectList(params);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("查询失败：" + e.getMessage());
        }
    }
    
    @GetMapping("/{id}")
    public Result<NbExpert> getById(@PathVariable String id) {
        try {
            return Result.success(expertService.selectById(id));
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("查询失败：" + e.getMessage());
        }
    }
    
    @PostMapping
    public Result<Void> add(@RequestBody NbExpert expert) {
        try {
            expertService.insert(expert);
            return Result.success("新增成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("新增失败：" + e.getMessage());
        }
    }
    
    @PutMapping
    public Result<Void> update(@RequestBody NbExpert expert) {
        try {
            expertService.update(expert);
            return Result.success("修改成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("修改失败：" + e.getMessage());
        }
    }
    
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        try {
            expertService.deleteById(id);
            return Result.success("删除成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("删除失败：" + e.getMessage());
        }
    }
    
    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        try {
            expertService.deleteBatch(ids);
            return Result.success("删除成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("删除失败：" + e.getMessage());
        }
    }
}

