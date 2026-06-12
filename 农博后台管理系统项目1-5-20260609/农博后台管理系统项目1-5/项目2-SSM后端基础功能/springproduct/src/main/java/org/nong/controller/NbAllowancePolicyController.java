package org.nong.controller;

import org.nong.common.PageQuery;
import org.nong.common.Result;
import org.nong.entity.NbAllowancePolicy;
import org.nong.service.INbAllowancePolicyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/yjnb/policy")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbAllowancePolicyController {

    @Autowired
    private INbAllowancePolicyService policyService;

    @GetMapping("/list")
    public Result<NbAllowancePolicy> list(PageQuery pageQuery,
                                          @RequestParam(required = false) String title,
                                          @RequestParam(required = false) String author,
                                          @RequestParam(required = false) Integer publishStatus,
                                          @RequestParam(required = false) Integer recommend) {
        return policyService.selectList(buildParams(pageQuery, title, author, publishStatus, recommend));
    }

    @GetMapping("/{id}")
    public Result<NbAllowancePolicy> getById(@PathVariable String id) {
        return Result.success(policyService.selectById(id));
    }

    @PostMapping
    public Result<Void> add(@RequestBody NbAllowancePolicy policy) {
        policyService.insert(policy);
        return Result.success("Added successfully");
    }

    @PutMapping
    public Result<Void> update(@RequestBody NbAllowancePolicy policy) {
        policyService.update(policy);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        policyService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        policyService.deleteBatch(ids);
        return Result.success("Deleted successfully");
    }

    @PostMapping("/recommendAllowancePolicy")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 1);
    }

    @PostMapping("/unrecommendAllowancePolicy")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 0);
    }

    @PostMapping("/releaseAllowancePolicy")
    public Result<Void> release(@RequestBody String[] ids) {
        return updatePublishStatus(ids, 1);
    }

    @PostMapping("/unreleaseAllowancePolicy")
    public Result<Void> unrelease(@RequestBody String[] ids) {
        return updatePublishStatus(ids, 0);
    }

    @PostMapping("/export")
    public Result<NbAllowancePolicy> export(@RequestParam(required = false) String title,
                                            @RequestParam(required = false) String author,
                                            @RequestParam(required = false) Integer publishStatus,
                                            @RequestParam(required = false) Integer recommend) {
        return policyService.selectList(buildParams(null, title, author, publishStatus, recommend));
    }

    private Result<Void> updateRecommend(String[] ids, int recommend) {
        int count = 0;
        for (String id : ids) {
            NbAllowancePolicy policy = new NbAllowancePolicy();
            policy.setId(id);
            policy.setRecommend(recommend);
            count += policyService.update(policy);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Result<Void> updatePublishStatus(String[] ids, int publishStatus) {
        int count = 0;
        for (String id : ids) {
            NbAllowancePolicy policy = new NbAllowancePolicy();
            policy.setId(id);
            policy.setPublishStatus(publishStatus);
            if (publishStatus == 1) {
                policy.setPublishTime(new Date());
            }
            count += policyService.update(policy);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Map<String, Object> buildParams(PageQuery pageQuery, String title, String author,
                                            Integer publishStatus, Integer recommend) {
        Map<String, Object> params = new HashMap<>();
        if (pageQuery != null) {
            params.put("offset", pageQuery.getOffset());
            params.put("pageSize", pageQuery.getPageSize());
        }
        params.put("title", title);
        params.put("author", author);
        params.put("publishStatus", publishStatus);
        params.put("recommend", recommend);
        return params;
    }
}
