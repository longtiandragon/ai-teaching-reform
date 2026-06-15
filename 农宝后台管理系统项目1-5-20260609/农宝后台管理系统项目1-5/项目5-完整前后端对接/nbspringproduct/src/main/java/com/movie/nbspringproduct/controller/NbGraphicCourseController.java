package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbGraphicCourse;
import com.movie.nbspringproduct.service.INbGraphicCourseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 图文课程Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/graphicCourse")
public class NbGraphicCourseController {
    
    @Autowired
    private INbGraphicCourseService graphicCourseService;
    
    /**
     * 查询图文课程列表
     */
    @GetMapping("/list")
    public Result<List<NbGraphicCourse>> list(NbGraphicCourse course) {
        List<NbGraphicCourse> list = graphicCourseService.selectGraphicCourseList(course);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取图文课程详细信息
     */
    @GetMapping("/{id}")
    public Result<NbGraphicCourse> getInfo(@PathVariable("id") String id) {
        return Result.success(graphicCourseService.getById(id));
    }
    
    /**
     * 新增图文课程
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbGraphicCourse course) {
        if (course.getBrowseNum() == null) {
            course.setBrowseNum(0);
        }
        if (course.getPublishStatus() == null) {
            course.setPublishStatus(0);
        }
        if (course.getRecommend() == null) {
            course.setRecommend(0);
        }
        return graphicCourseService.save(course) ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改图文课程
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbGraphicCourse course) {
        return graphicCourseService.updateById(course) ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除图文课程
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return graphicCourseService.removeByIds(java.util.Arrays.asList(ids)) ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
    
    /**
     * 推荐图文课程
     */
    @PostMapping("/recommend")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return graphicCourseService.recommendGraphicCourse(ids) > 0 ? 
                Result.success("推荐成功") : Result.error("推荐失败");
    }
    
    /**
     * 取消推荐图文课程
     */
    @PostMapping("/unrecommend")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return graphicCourseService.unrecommendGraphicCourse(ids) > 0 ? 
                Result.success("取消推荐成功") : Result.error("取消推荐失败");
    }
    
    /**
     * 发布图文课程
     */
    @PostMapping("/publish")
    public Result<Void> publish(@RequestBody String[] ids) {
        return graphicCourseService.publishGraphicCourse(ids) > 0 ? 
                Result.success("发布成功") : Result.error("发布失败");
    }
    
    /**
     * 取消发布图文课程
     */
    @PostMapping("/unpublish")
    public Result<Void> unpublish(@RequestBody String[] ids) {
        return graphicCourseService.unpublishGraphicCourse(ids) > 0 ? 
                Result.success("取消发布成功") : Result.error("取消发布失败");
    }
    
    /**
     * 导出图文课程列表
     */
    @PostMapping("/export")
    public Result<List<NbGraphicCourse>> export(NbGraphicCourse course) {
        List<NbGraphicCourse> list = graphicCourseService.selectGraphicCourseList(course);
        return Result.success(list);
    }
}


