package com.movie.nbspringproduct.controller;

import com.movie.nbspringproduct.common.Result;
import com.movie.nbspringproduct.entity.NbVideoCourse;
import com.movie.nbspringproduct.service.INbVideoCourseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 视频课程Controller
 */
@RestController
@RequestMapping("/dev-api/yjnb/videoCourse")
public class NbVideoCourseController {
    
    @Autowired
    private INbVideoCourseService videoCourseService;
    
    /**
     * 查询视频课程列表
     */
    @GetMapping("/list")
    public Result<List<NbVideoCourse>> list(NbVideoCourse course) {
        List<NbVideoCourse> list = videoCourseService.selectVideoCourseList(course);
        return Result.success(list, (long) list.size());
    }
    
    /**
     * 获取视频课程详细信息
     */
    @GetMapping("/{id}")
    public Result<NbVideoCourse> getInfo(@PathVariable("id") String id) {
        return Result.success(videoCourseService.getById(id));
    }
    
    /**
     * 新增视频课程
     */
    @PostMapping
    public Result<Void> add(@RequestBody NbVideoCourse course) {
        if (course.getBrowseNum() == null) {
            course.setBrowseNum(0);
        }
        if (course.getPublishStatus() == null) {
            course.setPublishStatus(0);
        }
        if (course.getRecommend() == null) {
            course.setRecommend(0);
        }
        return videoCourseService.save(course) ? 
                Result.success("新增成功") : Result.error("新增失败");
    }
    
    /**
     * 修改视频课程
     */
    @PutMapping
    public Result<Void> edit(@RequestBody NbVideoCourse course) {
        return videoCourseService.updateById(course) ? 
                Result.success("修改成功") : Result.error("修改失败");
    }
    
    /**
     * 删除视频课程
     */
    @DeleteMapping("/{ids}")
    public Result<Void> remove(@PathVariable String[] ids) {
        return videoCourseService.removeByIds(java.util.Arrays.asList(ids)) ? 
                Result.success("删除成功") : Result.error("删除失败");
    }
    
    /**
     * 推荐视频课程
     */
    @PostMapping("/recommend")
    public Result<Void> recommend(@RequestBody String[] ids) {
        return videoCourseService.recommendVideoCourse(ids) > 0 ? 
                Result.success("推荐成功") : Result.error("推荐失败");
    }
    
    /**
     * 取消推荐视频课程
     */
    @PostMapping("/unrecommend")
    public Result<Void> unrecommend(@RequestBody String[] ids) {
        return videoCourseService.unrecommendVideoCourse(ids) > 0 ? 
                Result.success("取消推荐成功") : Result.error("取消推荐失败");
    }
    
    /**
     * 发布视频课程
     */
    @PostMapping("/publish")
    public Result<Void> publish(@RequestBody String[] ids) {
        return videoCourseService.publishVideoCourse(ids) > 0 ? 
                Result.success("发布成功") : Result.error("发布失败");
    }
    
    /**
     * 取消发布视频课程
     */
    @PostMapping("/unpublish")
    public Result<Void> unpublish(@RequestBody String[] ids) {
        return videoCourseService.unpublishVideoCourse(ids) > 0 ? 
                Result.success("取消发布成功") : Result.error("取消发布失败");
    }
    
    /**
     * 导出视频课程列表
     */
    @PostMapping("/export")
    public Result<List<NbVideoCourse>> export(NbVideoCourse course) {
        List<NbVideoCourse> list = videoCourseService.selectVideoCourseList(course);
        return Result.success(list);
    }
}


