package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbGraphicCourse;
import com.movie.nbspringproduct.mapper.NbGraphicCourseMapper;
import com.movie.nbspringproduct.service.INbGraphicCourseService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Date;
import java.util.List;

/**
 * 图文课程Service实现类
 */
@Service
public class NbGraphicCourseServiceImpl extends ServiceImpl<NbGraphicCourseMapper, NbGraphicCourse> 
        implements INbGraphicCourseService {
    
    @Override
    public List<NbGraphicCourse> selectGraphicCourseList(NbGraphicCourse course) {
        LambdaQueryWrapper<NbGraphicCourse> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(course.getTitle()), NbGraphicCourse::getTitle, course.getTitle());
        wrapper.eq(StringUtils.isNotBlank(course.getTeacher()), NbGraphicCourse::getTeacher, course.getTeacher());
        wrapper.eq(StringUtils.isNotBlank(course.getCategory()), NbGraphicCourse::getCategory, course.getCategory());
        wrapper.eq(course.getPublishStatus() != null, NbGraphicCourse::getPublishStatus, course.getPublishStatus());
        wrapper.eq(course.getRecommend() != null, NbGraphicCourse::getRecommend, course.getRecommend());
        wrapper.orderByDesc(NbGraphicCourse::getCreateTime);
        return this.list(wrapper);
    }
    
    @Override
    public int recommendGraphicCourse(String[] ids) {
        List<NbGraphicCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbGraphicCourse course : list) {
            course.setRecommend(1);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unrecommendGraphicCourse(String[] ids) {
        List<NbGraphicCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbGraphicCourse course : list) {
            course.setRecommend(0);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int publishGraphicCourse(String[] ids) {
        List<NbGraphicCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbGraphicCourse course : list) {
            course.setPublishStatus(1);
            course.setPublishTime(new Date());
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unpublishGraphicCourse(String[] ids) {
        List<NbGraphicCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbGraphicCourse course : list) {
            course.setPublishStatus(0);
            course.setPublishTime(null);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
}


