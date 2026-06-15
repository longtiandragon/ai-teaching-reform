package com.movie.nbspringproduct.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.movie.nbspringproduct.entity.SysRole;
import com.movie.nbspringproduct.mapper.SysRoleMapper;
import com.movie.nbspringproduct.service.ISysRoleService;
import org.springframework.stereotype.Service;

/**
 * 角色Service实现类
 */
@Service
public class SysRoleServiceImpl extends ServiceImpl<SysRoleMapper, SysRole> implements ISysRoleService {
}

