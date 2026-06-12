package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbCreditLoan;
import com.movie.nbspringproduct.service.INbCreditLoanService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 信贷信息Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/loan")
public class NbCreditLoanController {
    
    @Autowired
    private INbCreditLoanService creditLoanService;
    
    /**
     * 查询信贷信息列表
     */
    @GetMapping("/list")
    public Result<List<NbCreditLoan>> list(NbCreditLoan loan) {
        List<NbCreditLoan> list = creditLoanService.selectCreditLoanList(loan);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取信贷信息详细信息
     */
    @GetMapping("/{id}")
    public Result<NbCreditLoan> getInfo(@PathVariable("id") String id) {
        return Result.success(creditLoanService.selectCreditLoanById(id));
    }
    
    /**
     * 新增信贷信息
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbCreditLoan loan) {
        return creditLoanService.insertCreditLoan(loan) > 0 ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改信贷信息
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbCreditLoan loan) {
        return creditLoanService.updateCreditLoan(loan) > 0 ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除信贷信息
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return creditLoanService.deleteCreditLoanByIds(ids) > 0 ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
    
    /**
     * 推荐信贷信息
     */
    @PostMapping("/recommandCreditLoan")
    public Result<Void> recommand(@RequestBody String[] ids) {
        return creditLoanService.recommandCreditLoan(ids) > 0 ? 
                Result.success("推荐成功") : Result.error("推荐失败");
    }
    
    /**
     * 取消推荐信贷信息
     */
    @PostMapping("/unRecommandCreditLoan")
    public Result<Void> unRecommand(@RequestBody String[] ids) {
        return creditLoanService.unRecommandCreditLoan(ids) > 0 ? 
                Result.success("取消推荐成功") : Result.error("取消推荐失败");
    }
    
    /**
     * 发布信贷信息
     */
    @PostMapping("/publishCreditLoan")
    public Result<Void> publish(@RequestBody String[] ids) {
        return creditLoanService.publishCreditLoan(ids) > 0 ? 
                Result.success("发布成功") : Result.error("发布失败");
    }
    
    /**
     * 取消发布信贷信息
     */
    @PostMapping("/unPublishCreditLoan")
    public Result<Void> unPublish(@RequestBody String[] ids) {
        return creditLoanService.unPublishCreditLoan(ids) > 0 ? 
                Result.success("取消发布成功") : Result.error("取消发布失败");
    }
    
    /**
     * 导出信贷信息列表
     */
    @PostMapping("/export")
    public Result<List<NbCreditLoan>> export(NbCreditLoan loan) {
        List<NbCreditLoan> list = creditLoanService.selectCreditLoanList(loan);
        return Result.success(list);
    }
}

