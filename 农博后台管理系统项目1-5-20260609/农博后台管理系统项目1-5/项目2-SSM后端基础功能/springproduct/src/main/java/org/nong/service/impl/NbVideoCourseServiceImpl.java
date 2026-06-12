package org.nong.service.impl;

import org.nong.common.Result;
import org.nong.entity.NbVideoCourse;
import org.nong.mapper.NbVideoCourseMapper;
import org.nong.service.INbVideoCourseService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class NbVideoCourseServiceImpl implements INbVideoCourseService {
    
    @Autowired
    private NbVideoCourseMapper courseMapper;
    
    @Override
    @SuppressWarnings("unchecked")
    public Result<NbVideoCourse> selectList(Map<String, Object> params) {
        List<NbVideoCourse> list = courseMapper.selectList(params);
        Long total = courseMapper.selectCount(params);
        Result result = Result.success();
        result.setRows(list);
        result.setTotal(total);
        result.buildPageData();
        return result;
    }
    
    @Override
    public NbVideoCourse selectById(String id) {
        return courseMapper.selectById(id);
    }
    
    @Override
    public int insert(NbVideoCourse course) {
        if (course.getId() == null || course.getId().isEmpty()) {
            course.setId(UUID.randomUUID().toString().replace("-", ""));
        }
        return courseMapper.insert(course);
    }
    
    @Override
    public int update(NbVideoCourse course) {
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

