package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbGraphicCourse;
import org.nong.mapper.NbGraphicCourseMapper;
import org.nong.service.INbGraphicCourseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class NbGraphicCourseServiceImpl implements INbGraphicCourseService {
    
    @Autowired
    private NbGraphicCourseMapper courseMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbGraphicCourse> selectList(Map<String, Object> params) {
        List<NbGraphicCourse> list = courseMapper.selectList(params);
        Long total = courseMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbGraphicCourse selectById(String id) {
        return courseMapper.selectById(id);
    }
    
    @Override
    public int insert(NbGraphicCourse course) {
        if (course.getId() == null || course.getId().isEmpty()) {
            course.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return courseMapper.insert(course);
    }
    
    @Override
    public int update(NbGraphicCourse course) {
        return courseMapper.update(course);
    }
    
    @Override
    public int deleteById(String id) {
        return courseMapper.deleteById(id);
    }
    
    @Override
    public int deleteBatch(String[] ids) {
        return courseMapper.deleteBatch(ids);
    }
}

