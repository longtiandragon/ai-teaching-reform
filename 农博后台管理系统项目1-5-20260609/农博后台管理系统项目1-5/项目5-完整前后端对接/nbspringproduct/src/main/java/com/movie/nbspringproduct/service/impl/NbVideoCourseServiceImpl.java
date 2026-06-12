package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbVideoCourse;
import com.movie.nbspringproduct.mapper.NbVideoCourseMapper;
import com.movie.nbspringproduct.service.INbVideoCourseService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Date;
import java.util.List;

/**
 * 视频课程Service实现类
 */
@Service
public class NbVideoCourseServiceImpl extends ServiceImpl<NbVideoCourseMapper, NbVideoCourse> 
        implements INbVideoCourseService {
    
    @Override
    public List<NbVideoCourse> selectVideoCourseList(NbVideoCourse course) {
        LambdaQueryWrapper<NbVideoCourse> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(course.getTitle()), NbVideoCourse::getTitle, course.getTitle());
        wrapper.eq(StringUtils.isNotBlank(course.getTeacher()), NbVideoCourse::getTeacher, course.getTeacher());
        wrapper.eq(StringUtils.isNotBlank(course.getCategory()), NbVideoCourse::getCategory, course.getCategory());
        wrapper.eq(course.getPublishStatus() != null, NbVideoCourse::getPublishStatus, course.getPublishStatus());
        wrapper.eq(course.getRecommend() != null, NbVideoCourse::getRecommend, course.getRecommend());
        wrapper.orderByDesc(NbVideoCourse::getCreateTime);
        return this.list(wrapper);
    }
    
    @Override
    public int recommendVideoCourse(String[] ids) {
        List<NbVideoCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbVideoCourse course : list) {
            course.setRecommend(1);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unrecommendVideoCourse(String[] ids) {
        List<NbVideoCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbVideoCourse course : list) {
            course.setRecommend(0);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int publishVideoCourse(String[] ids) {
        List<NbVideoCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbVideoCourse course : list) {
            course.setPublishStatus(1);
            course.setPublishTime(new Date());
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
    
    @Override
    public int unpublishVideoCourse(String[] ids) {
        List<NbVideoCourse> list = this.listByIds(Arrays.asList(ids));
        for (NbVideoCourse course : list) {
            course.setPublishStatus(0);
            course.setPublishTime(null);
        }
        return this.updateBatchById(list) ? 1 : 0;
    }
}


