package org.nong.controller;

import org.nong.common.PageQuery;
import org.nong.common.Result;
import org.nong.entity.NbAdvertisement;
import org.nong.service.INbAdvertisementService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/yjnb/advertisement")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbAdvertisementController {

    @Autowired
    private INbAdvertisementService adService;

    @GetMapping("/list")
    public Result<NbAdvertisement> list(PageQuery pageQuery,
                                        @RequestParam(required = false) String title,
                                        @RequestParam(required = false) String position,
                                        @RequestParam(required = false) Integer status) {
        return adService.selectList(buildParams(pageQuery, title, position, status));
    }

    @GetMapping("/{id}")
    public Result<NbAdvertisement> getById(@PathVariable String id) {
        return Result.success(adService.selectById(id));
    }

    @PostMapping
    public Result<Void> add(@RequestBody NbAdvertisement ad) {
        adService.insert(ad);
        return Result.success("Added successfully");
    }

    @PutMapping
    public Result<Void> update(@RequestBody NbAdvertisement ad) {
        adService.update(ad);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        adService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        adService.deleteBatch(ids);
        return Result.success("Deleted successfully");
    }

    @PostMapping("/publish")
    public Result<Void> publish(@RequestBody String[] ids) {
        return updateStatus(ids, 1);
    }

    @PostMapping("/unpublish")
    public Result<Void> unpublish(@RequestBody String[] ids) {
        return updateStatus(ids, 0);
    }

    @PostMapping("/export")
    public Result<NbAdvertisement> export(@RequestParam(required = false) String title,
                                          @RequestParam(required = false) String position,
                                          @RequestParam(required = false) Integer status) {
        return adService.selectList(buildParams(null, title, position, status));
    }

    private Result<Void> updateStatus(String[] ids, int status) {
        int count = 0;
        for (String id : ids) {
            NbAdvertisement ad = new NbAdvertisement();
            ad.setId(id);
            ad.setStatus(status);
            count += adService.update(ad);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Map<String, Object> buildParams(PageQuery pageQuery, String title, String position, Integer status) {
        Map<String, Object> params = new HashMap<>();
        if (pageQuery != null) {
            params.put("offset", pageQuery.getOffset());
            params.put("pageSize", pageQuery.getPageSize());
        }
        params.put("title", title);
        params.put("position", position);
        params.put("status", status);
        return params;
    }
}
