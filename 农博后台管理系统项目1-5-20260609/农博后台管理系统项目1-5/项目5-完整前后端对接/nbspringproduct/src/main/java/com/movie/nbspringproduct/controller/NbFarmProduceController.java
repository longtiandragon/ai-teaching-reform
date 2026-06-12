package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbFarmProduce;
import com.movie.nbspringproduct.service.INbFarmProduceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 农产品Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/produce")
public class NbFarmProduceController {
    
    @Autowired
    private INbFarmProduceService farmProduceService;
    
    /**
     * 查询农产品列表
     */
    @GetMapping("/list")
    public Result<List<NbFarmProduce>> list(NbFarmProduce produce) {
        List<NbFarmProduce> list = farmProduceService.selectFarmProduceList(produce);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取农产品详细信息
     */
    @GetMapping("/{id}")
    public Result<NbFarmProduce> getInfo(@PathVariable("id") String id) {
        return Result.success(farmProduceService.selectFarmProduceById(id));
    }
    
    /**
     * 新增农产品
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbFarmProduce produce) {
        return farmProduceService.insertFarmProduce(produce) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改农产品
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbFarmProduce produce) {
        return farmProduceService.updateFarmProduce(produce) > 0 ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除农产品
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return farmProduceService.deleteFarmProduceByIds(ids) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
    
    /**
     * 推荐农产品
     */
    @PostMapping("/recommendFarmProduce")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return farmProduceService.recommendFarmProduce(ids) > 0 ? 
                Result.success("推荐成功") : Result.error("推荐失败");
    }
    
    /**
     * 取消推荐农产品
     */
    @PostMapping("/unrecommendFarmProduce")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return farmProduceService.unrecommendFarmProduce(ids) > 0 ? 
                Result.success("取消推荐成功") : Result.error("取消推荐失败");
    }
    
    /**
     * 发布农产品
     */
    @PostMapping("/pushFarmProduce")
    public Result<Void> push(@RequestBody String[] ids) {
        return farmProduceService.pushFarmProduce(ids) > 0 ? 
                Result.success("发布成功") : Result.error("发布失败");
    }
    
    /**
     * 取消发布农产品
     */
    @PostMapping("/unpushFarmProduce")
    public Result<Void> unpush(@RequestBody String[] ids) {
        return farmProduceService.unpushFarmProduce(ids) > 0 ? 
                Result.success("取消发布成功") : Result.error("取消发布失败");
    }
    
    /**
     * 导出农产品列表
     */
    @PostMapping("/export")
    public Result<List<NbFarmProduce>> export(NbFarmProduce produce) {
        List<NbFarmProduce> list = farmProduceService.selectFarmProduceList(produce);
        return Result.success(list);
    }
}

