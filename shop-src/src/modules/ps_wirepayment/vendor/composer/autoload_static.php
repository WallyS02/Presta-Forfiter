<?php

// autoload_static.php @generated by Composer

namespace Composer\Autoload;

class ComposerStaticInit3da919382ae498fb29b3e1fabf079aa0
{
    public static $classMap = array (
        'Ps_Wirepayment' => __DIR__ . '/../..' . '/ps_wirepayment.php',
    );

    public static function getInitializer(ClassLoader $loader)
    {
        return \Closure::bind(function () use ($loader) {
            $loader->classMap = ComposerStaticInit3da919382ae498fb29b3e1fabf079aa0::$classMap;

        }, null, ClassLoader::class);
    }
}
