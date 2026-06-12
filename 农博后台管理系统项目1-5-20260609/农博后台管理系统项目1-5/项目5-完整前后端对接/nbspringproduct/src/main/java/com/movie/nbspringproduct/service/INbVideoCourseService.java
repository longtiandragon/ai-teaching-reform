package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbVideoCourse;

import java.util.List;

/**
 * 视频课程Service接口
 */
public interface INbVideoCourseService extends IService<NbVideoCourse> {
    
    /**
     * 查询视频课程列表
     * @param videoCourse 查询条件
     * @return 视频课程列表
     */
    List<NbVideoCourse> selectVideoCourseList(NbVideoCourse videoCourse);
    
    /**
     * 推荐视频课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int recommendVideoCourse(String[] ids);
    
    /**
     * 取消推荐视频课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int unrecommendVideoCourse(String[] ids);
    
    /**
     * 发布视频课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int publishVideoCourse(String[] ids);
    
    /**
     * 取消发布视频课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int unpublishVideoCourse(String[] ids);
}


