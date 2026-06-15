package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbAllowancePolicy;
import com.movie.nbspringproduct.service.INbAllowancePolicyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 补贴政策Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/policy")
public class NbAllowancePolicyController {
    
    @Autowired
    private INbAllowancePolicyService allowancePolicyService;
    
    /**
     * 查询补贴政策列表
     */
    @GetMapping("/list")
    public Result<List<NbAllowancePolicy>> list(NbAllowancePolicy policy) {
        List<NbAllowancePolicy> list = allowancePolicyService.selectAllowancePolicyList(policy);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取补贴政策详细信息
     */
    @GetMapping("/{id}")
    public Result<NbAllowancePolicy> getInfo(@PathVariable("id") String id) {
        return Result.success(allowancePolicyService.selectAllowancePolicyById(id));
    }
    
    /**
     * 新增补贴政策
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbAllowancePolicy policy) {
        return allowancePolicyService.insertAllowancePolicy(policy) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改补贴政策
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbAllowancePolicy policy) {
        return allowancePolicyService.updateAllowancePolicy(policy) > 0 ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除补贴政策
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return allowancePolicyService.deleteAllowancePolicyByIds(ids) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
    
    /**
     * 推荐补贴政策
     */
    @PostMapping("/recommendAllowancePolicy")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return allowancePolicyService.recommendAllowancePolicy(ids) > 0 ? 
                Result.success("推荐成功") : Result.error("推荐失败");
    }
    
    /**
     * 取消推荐补贴政策
     */
    @PostMapping("/unrecommendAllowancePolicy")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return allowancePolicyService.unrecommendAllowancePolicy(ids) > 0 ? 
                Result.success("取消推荐成功") : Result.error("取消推荐失败");
    }
    
    /**
     * 发布补贴政策
     */
    @PostMapping("/releaseAllowancePolicy")
    public Result<Void> release(@RequestBody String[] ids) {
        return allowancePolicyService.releaseAllowancePolicy(ids) > 0 ? 
                Result.success("发布成功") : Result.error("发布失败");
    }
    
    /**
     * 取消发布补贴政策
     */
    @PostMapping("/unreleaseAllowancePolicy")
    public Result<Void> unrelease(@RequestBody String[] ids) {
        return allowancePolicyService.unreleaseAllowancePolicy(ids) > 0 ? 
                Result.success("取消发布成功") : Result.error("取消发布失败");
    }
    
    /**
     * 导出补贴政策列表
     */
    @PostMapping("/export")
    public Result<List<NbAllowancePolicy>> export(NbAllowancePolicy policy) {
        List<NbAllowancePolicy> list = allowancePolicyService.selectAllowancePolicyList(policy);
        return Result.success(list);
    }
}

