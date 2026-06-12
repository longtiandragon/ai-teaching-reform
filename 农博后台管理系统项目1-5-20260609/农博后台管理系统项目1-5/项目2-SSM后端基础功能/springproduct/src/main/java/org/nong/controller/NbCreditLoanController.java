package org.nong.controller;

import org.nong.common.PageQuery;
import org.nong.common.Result;
import org.nong.entity.NbCreditLoan;
import org.nong.service.INbCreditLoanService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/yjnb/loan")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbCreditLoanController {

    @Autowired
    private INbCreditLoanService loanService;

    @GetMapping("/list")
    public Result<NbCreditLoan> list(PageQuery pageQuery,
                                     @RequestParam(required = false) String title,
                                     @RequestParam(required = false) String author,
                                     @RequestParam(required = false) Integer publishStatus,
                                     @RequestParam(required = false) Integer recommend) {
        return loanService.selectList(buildParams(pageQuery, title, author, publishStatus, recommend));
    }

    @GetMapping("/{id}")
    public Result<NbCreditLoan> getById(@PathVariable String id) {
        return Result.success(loanService.selectById(id));
    }

    @PostMapping
    public Result<Void> add(@RequestBody NbCreditLoan loan) {
        loanService.insert(loan);
        return Result.success("Added successfully");
    }

    @PutMapping
    public Result<Void> update(@RequestBody NbCreditLoan loan) {
        loanService.update(loan);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        loanService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        loanService.deleteBatch(ids);
        return Result.success("Deleted successfully");
    }

    @PostMapping("/recommandCreditLoan")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 1);
    }

    @PostMapping("/unRecommandCreditLoan")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 0);
    }

    @PostMapping("/publishCreditLoan")
    public Result<Void> publish(@RequestBody String[] ids) {
        return updatePublishStatus(ids, 1);
    }

    @PostMapping("/unPublishCreditLoan")
    public Result<Void> unpublish(@RequestBody String[] ids) {
        return updatePublishStatus(ids, 0);
    }

    @PostMapping("/export")
    public Result<NbCreditLoan> export(@RequestParam(required = false) String title,
                                       @RequestParam(required = false) String author,
                                       @RequestParam(required = false) Integer publishStatus,
                                       @RequestParam(required = false) Integer recommend) {
        return loanService.selectList(buildParams(null, title, author, publishStatus, recommend));
    }

    private Result<Void> updateRecommend(String[] ids, int recommend) {
        int count = 0;
        for (String id : ids) {
            NbCreditLoan loan = new NbCreditLoan();
            loan.setId(id);
            loan.setRecommend(recommend);
            count += loanService.update(loan);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Result<Void> updatePublishStatus(String[] ids, int publishStatus) {
        int count = 0;
        for (String id : ids) {
            NbCreditLoan loan = new NbCreditLoan();
            loan.setId(id);
            loan.setPublishStatus(publishStatus);
            if (publishStatus == 1) {
                loan.setPublishTime(new Date());
            }
            count += loanService.update(loan);
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
