package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbExpert;
import com.movie.nbspringproduct.mapper.NbExpertMapper;
import com.movie.nbspringproduct.service.INbExpertService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;

/**
 * 专家Service实现类
 */
@Service
public class NbExpertServiceImpl extends ServiceImpl<NbExpertMapper, NbExpert> 
        implements INbExpertService {
    
    @Override
    public List<NbExpert> selectExpertList(NbExpert expert) {
        LambdaQueryWrapper<NbExpert> wrapper = new LambdaQueryWrapper<>();
        
        wrapper.like(StringUtils.isNotBlank(expert.getName()), 
                NbExpert::getName, expert.getName());
        wrapper.like(StringUtils.isNotBlank(expert.getSpecialty()), 
                NbExpert::getSpecialty, expert.getSpecialty());
        wrapper.eq(expert.getStatus() != null, 
                NbExpert::getStatus, expert.getStatus());
        
        wrapper.orderByDesc(NbExpert::getCreateTime);
        
        return this.list(wrapper);
    }
    
    @Override
    public NbExpert selectExpertById(String id) {
        return this.getById(id);
    }
    
    @Override
    public int insertExpert(NbExpert expert) {
        if (expert.getServiceCount() == null) {
            expert.setServiceCount(0);
        }
        if (expert.getStatus() == null) {
            expert.setStatus(1);
        }
        return this.save(expert) ? 1 : 0;
    }
    
    @Override
    public int updateExpert(NbExpert expert) {
        return this.updateById(expert) ? 1 : 0;
    }
    
    @Override
    public int deleteExpertByIds(String[] ids) {
        return this.removeByIds(Arrays.asList(ids)) ? 1 : 0;
    }
}

