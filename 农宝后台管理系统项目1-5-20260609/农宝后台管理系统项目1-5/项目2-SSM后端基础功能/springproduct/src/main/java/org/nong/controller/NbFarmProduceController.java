package org.nong.controller;

import org.nong.common.PageQuery;
import org.nong.common.Result;
import org.nong.entity.NbFarmProduce;
import org.nong.service.INbFarmProduceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/yjnb/produce")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbFarmProduceController {

    @Autowired
    private INbFarmProduceService produceService;

    @GetMapping("/list")
    public Result<NbFarmProduce> list(PageQuery pageQuery,
                                      @RequestParam(required = false) String title,
                                      @RequestParam(required = false) String catgory,
                                      @RequestParam(required = false) String providerName,
                                      @RequestParam(required = false) Integer pushStatus,
                                      @RequestParam(required = false) Integer recommend) {
        Map<String, Object> params = buildParams(pageQuery, title, catgory, providerName, pushStatus, recommend);
        return produceService.selectList(params);
    }

    @GetMapping("/{id}")
    public Result<NbFarmProduce> getById(@PathVariable String id) {
        return Result.success(produceService.selectById(id));
    }

    @PostMapping
    public Result<Void> add(@RequestBody NbFarmProduce produce) {
        produceService.insert(produce);
        return Result.success("Added successfully");
    }

    @PutMapping
    public Result<Void> update(@RequestBody NbFarmProduce produce) {
        produceService.update(produce);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        produceService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        produceService.deleteBatch(ids);
        return Result.success("Deleted successfully");
    }

    @PostMapping("/recommendFarmProduce")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 1);
    }

    @PostMapping("/unrecommendFarmProduce")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 0);
    }

    @PostMapping("/pushFarmProduce")
    public Result<Void> push(@RequestBody String[] ids) {
        return updatePushStatus(ids, 1);
    }

    @PostMapping("/unpushFarmProduce")
    public Result<Void> unpush(@RequestBody String[] ids) {
        return updatePushStatus(ids, 0);
    }

    @PostMapping("/export")
    public Result<NbFarmProduce> export(@RequestParam(required = false) String title,
                                        @RequestParam(required = false) String catgory,
                                        @RequestParam(required = false) String providerName,
                                        @RequestParam(required = false) Integer pushStatus,
                                        @RequestParam(required = false) Integer recommend) {
        Map<String, Object> params = buildParams(null, title, catgory, providerName, pushStatus, recommend);
        return produceService.selectList(params);
    }

    private Result<Void> updateRecommend(String[] ids, int recommend) {
        int count = 0;
        for (String id : ids) {
            NbFarmProduce produce = new NbFarmProduce();
            produce.setId(id);
            produce.setRecommend(recommend);
            count += produceService.update(produce);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Result<Void> updatePushStatus(String[] ids, int pushStatus) {
        int count = 0;
        for (String id : ids) {
            NbFarmProduce produce = new NbFarmProduce();
            produce.setId(id);
            produce.setPushStatus(pushStatus);
            if (pushStatus == 1) {
                produce.setPushTime(new Date());
            }
            count += produceService.update(produce);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Map<String, Object> buildParams(PageQuery pageQuery, String title, String catgory,
                                            String providerName, Integer pushStatus, Integer recommend) {
        Map<String, Object> params = new HashMap<>();
        if (pageQuery != null) {
            params.put("offset", pageQuery.getOffset());
            params.put("pageSize", pageQuery.getPageSize());
        }
        params.put("title", title);
        params.put("catgory", catgory);
        params.put("providerName", providerName);
        params.put("pushStatus", pushStatus);
        params.put("recommend", recommend);
        return params;
    }
}
