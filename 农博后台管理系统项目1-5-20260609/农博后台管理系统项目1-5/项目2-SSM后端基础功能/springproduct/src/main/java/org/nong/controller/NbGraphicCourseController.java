package org.nong.controller;

import org.nong.common.PageQuery;
import org.nong.common.Result;
import org.nong.entity.NbGraphicCourse;
import org.nong.service.INbGraphicCourseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/yjnb/graphicCourse")
@CrossOrigin(originPatterns = "*", allowCredentials = "true")
public class NbGraphicCourseController {

    @Autowired
    private INbGraphicCourseService courseService;

    @GetMapping("/list")
    public Result<NbGraphicCourse> list(PageQuery pageQuery,
                                        @RequestParam(required = false) String title,
                                        @RequestParam(required = false) String teacher,
                                        @RequestParam(required = false) String category,
                                        @RequestParam(required = false) Integer publishStatus,
                                        @RequestParam(required = false) Integer recommend) {
        return courseService.selectList(buildParams(pageQuery, title, teacher, category, publishStatus, recommend));
    }

    @GetMapping("/{id}")
    public Result<NbGraphicCourse> getById(@PathVariable String id) {
        return Result.success(courseService.selectById(id));
    }

    @PostMapping
    public Result<Void> add(@RequestBody NbGraphicCourse course) {
        courseService.insert(course);
        return Result.success("Added successfully");
    }

    @PutMapping
    public Result<Void> update(@RequestBody NbGraphicCourse course) {
        courseService.update(course);
        return Result.success("Updated successfully");
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable String id) {
        courseService.deleteById(id);
        return Result.success("Deleted successfully");
    }

    @DeleteMapping("/batch")
    public Result<Void> deleteBatch(@RequestBody String[] ids) {
        courseService.deleteBatch(ids);
        return Result.success("Deleted successfully");
    }

    @PostMapping("/recommend")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 1);
    }

    @PostMapping("/unrecommend")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return updateRecommend(ids, 0);
    }

    @PostMapping("/publish")
    public Result<Void> publish(@RequestBody String[] ids) {
        return updatePublishStatus(ids, 1);
    }

    @PostMapping("/unpublish")
    public Result<Void> unpublish(@RequestBody String[] ids) {
        return updatePublishStatus(ids, 0);
    }

    @PostMapping("/export")
    public Result<NbGraphicCourse> export(@RequestParam(required = false) String title,
                                          @RequestParam(required = false) String teacher,
                                          @RequestParam(required = false) String category,
                                          @RequestParam(required = false) Integer publishStatus,
                                          @RequestParam(required = false) Integer recommend) {
        return courseService.selectList(buildParams(null, title, teacher, category, publishStatus, recommend));
    }

    private Result<Void> updateRecommend(String[] ids, int recommend) {
        int count = 0;
        for (String id : ids) {
            NbGraphicCourse course = new NbGraphicCourse();
            course.setId(id);
            course.setRecommend(recommend);
            count += courseService.update(course);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Result<Void> updatePublishStatus(String[] ids, int publishStatus) {
        int count = 0;
        for (String id : ids) {
            NbGraphicCourse course = new NbGraphicCourse();
            course.setId(id);
            course.setPublishStatus(publishStatus);
            if (publishStatus == 1) {
                course.setPublishTime(new Date());
            }
            count += courseService.update(course);
        }
        return count > 0 ? Result.success("Updated successfully") : Result.error("Update failed");
    }

    private Map<String, Object> buildParams(PageQuery pageQuery, String title, String teacher,
                                            String category, Integer publishStatus, Integer recommend) {
        Map<String, Object> params = new HashMap<>();
        if (pageQuery != null) {
            params.put("offset", pageQuery.getOffset());
            params.put("pageSize", pageQuery.getPageSize());
        }
        params.put("title", title);
        params.put("teacher", teacher);
        params.put("category", category);
        params.put("publishStatus", publishStatus);
        params.put("recommend", recommend);
        return params;
    }
}
