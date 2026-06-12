package com.movie.nbspringproduct.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.movie.nbspringproduct.entity.NbGraphicCourse;

import java.util.List;

/**
 * 图文课程Service接口
 */
public interface INbGraphicCourseService extends IService<NbGraphicCourse> {
    
    /**
     * 查询图文课程列表
     * @param graphicCourse 查询条件
     * @return 图文课程列表
     */
    List<NbGraphicCourse> selectGraphicCourseList(NbGraphicCourse graphicCourse);
    
    /**
     * 推荐图文课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int recommendGraphicCourse(String[] ids);
    
    /**
     * 取消推荐图文课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int unrecommendGraphicCourse(String[] ids);
    
    /**
     * 发布图文课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int publishGraphicCourse(String[] ids);
    
    /**
     * 取消发布图文课程
     * @param ids 课程ID数组
     * @return 结果
     */
    int unpublishGraphicCourse(String[] ids);
}


