package Ditaa;

sub strict;
sub warnings;

use File::Temp;

sub new {
    my $class = shift;

    my %args = (@_ % 2) == 0? @_: {};

    return bless {
        _bin_path => $args{bin} || undef,
        _java_path => $args{java} || undef,
    }, $class;
}

# accessors
sub bin_path {
    $_[0]->{_bin_path} = $_[1] if $_[1];
    return shift->{_bin_path};
}

sub java_path {
    $_[0]->{_java_path} = $_[1] if $_[1];
    return shift->{_java_path};
}


# methods
sub render_image {
    my ($self, $input, $output) = @_;

    # error ditaa
    die "error: ditaa binary not found"
        unless (-e $self->bin_path);

    # error java
    die "error: java virtual machine binary not found"
        unless (-e $self->java_path);

    my $filename = $self->_temp_file($input);

    system $self->_make_command($filename, $output); 

    # error image not found
    die "error: image cannot be created" 
        unless (-e $output);
}

sub _temp_file {
    my ($self, $input) = @_;

    my $temp = File::Temp->new(UNLINK => 0);
    print $temp $input;
    $temp->seek(0, SEEK_END);

    return $temp->filename;
}

sub _make_command {
    my ($self, $input, $output) = @_;

    return join ' ', (
        $self->java_path,
        "-jar",
        "'". $self->bin_path ."'",
        "'". $input ."'",
        "'". $output ."'",
    );
}


1;

__END__

=pod

=head1 NAME

Ditaa - Perl Ditaa Class Implementation


=head1 SYNOPSIS

    use Ditaa;

    # new ditaa instance
    my $ditaa = Ditaa->new(
        bin => '/path/to/binary/ditaa',
        java => '/path/to/binary/java',
    );

    # ditaa string 
    my $input = qq{
        /--------------------\
        | This is only a test|
        \--------------------/
    };

    # rendering ditaa image
    $ditaa->render_image($input, '/path/to/output/filename.png');


=head1 DESCRIPTION

This module is a simple wrapper that invoke java virtual machine and use ditaa
command line tool to convert a simple text into a flowchart image.

=head1 Accessors

=head3 bin_path

Acessor to get or set ditaa binary path

    $ditaa->bin_path('/usr/bin/ditaa');
    say $ditaa->bin_path;

=head3 java_path

Acessor to get or set java virtual machine path

    $ditaa->java_path('/usr/bin/java');
    say $ditaa->java_path;


=head1 Methods

=head3 render_image

Method to pass informations for image render

    # render image
    $ditaa->render_image( $input, $output );


=head1 AUTHOR

2013 (c) Bivee L<http://bivee.com.br>

Daniel Vinciguerra <daniel.vinciguerra@bivee.com.br>


=head3 COPYRIGHT AND LICENSE

This software is copyright (c) 2013 by Bivee.

This is a free software; you can redistribute it and/or modify it under the same terms of Perl 5 programming 
languagem system itself.

=cut
