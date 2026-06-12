package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbExpert;
import com.movie.nbspringproduct.service.INbExpertService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 专家Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/expert")
public class NbExpertController {
    
    @Autowired
    private INbExpertService expertService;
    
    /**
     * 查询专家列表
     */
    @GetMapping("/list")
    public Result<List<NbExpert>> list(NbExpert expert) {
        List<NbExpert> list = expertService.selectExpertList(expert);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取专家详细信息
     */
    @GetMapping("/{id}")
    public Result<NbExpert> getInfo(@PathVariable("id") String id) {
        return Result.success(expertService.selectExpertById(id));
    }
    
    /**
     * 新增专家
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbExpert expert) {
        return expertService.insertExpert(expert) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改专家
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbExpert expert) {
        return expertService.updateExpert(expert) > 0 ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除专家
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return expertService.deleteExpertByIds(ids) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
}

