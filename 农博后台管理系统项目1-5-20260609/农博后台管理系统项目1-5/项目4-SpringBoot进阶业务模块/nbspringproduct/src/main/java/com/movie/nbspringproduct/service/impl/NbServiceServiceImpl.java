package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.NbService;
import com.movie.nbspringproduct.mapper.NbServiceMapper;
import com.movie.nbspringproduct.service.INbServiceService;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;

/**
 * 服务Service实现类
 */
@Service
public class NbServiceServiceImpl extends ServiceImpl<NbServiceMapper, NbService> 
        implements INbServiceService {
    
    @Override
    public List<NbService> selectServiceList(NbService service) {
        LambdaQueryWrapper<NbService> wrapper = new LambdaQueryWrapper<>();
        
        wrapper.like(StringUtils.isNotBlank(service.getTitle()), 
                NbService::getTitle, service.getTitle());
        wrapper.eq(StringUtils.isNotBlank(service.getCategory()), 
                NbService::getCategory, service.getCategory());
        wrapper.eq(service.getStatus() != null, 
                NbService::getStatus, service.getStatus());
        
        wrapper.orderByDesc(NbService::getCreateTime);
        
        return this.list(wrapper);
    }
    
    @Override
    public NbService selectServiceById(String id) {
        return this.getById(id);
    }
    
    @Override
    public int insertService(NbService service) {
        if (service.getOrderCount() == null) {
            service.setOrderCount(0);
        }
        if (service.getStatus() == null) {
            service.setStatus(1);
        }
        return this.save(service) ? 1 : 0;
    }
    
    @Override
    public int updateService(NbService service) {
        return this.updateById(service) ? 1 : 0;
    }
    
    @Override
    public int deleteServiceByIds(String[] ids) {
        return this.removeByIds(Arrays.asList(ids)) ? 1 : 0;
    }
}

